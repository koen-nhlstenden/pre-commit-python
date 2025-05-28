import logging
import os
import time

import paramiko
from dotenv import load_dotenv

from info import FileInfo
from utils import Logger

from hooks.fix_docs import process_file

load_dotenv()
logging.getLogger("paramiko").setLevel(logging.WARNING)


class SSHConnection:
    """
    Manages an SSH connection to a remote server and provides methods for file operations via SFTP and command execution.

    Attributes:
        ip (str): The IP address of the remote server.
        client (paramiko.SSHClient): The SSH client for executing commands.
        sftp_client (paramiko.SFTPClient): The SFTP client for file operations.
        logger (logging.Logger): Logger for logging messages.
        info (FileInfo | None): Stores additional metadata.
    """
    def __init__(self, ip: str, username: str = None, password: str = None):
        """
        Initializes the SSH connection.

        :param ip: The IP address of the remote server.
        :param username: SSH username (optional, defaults to environment variable VM_USER).
        :param password: SSH password (optional, defaults to environment variable VM_PASSWORD).
        """
        self.logger = Logger.setup_logger()
        self.ip = ip
        self.info = None

        # Load credentials from environment if not provided
        username = username or os.getenv("VM_USER")
        password = password or os.getenv("VM_PASSWORD")

        # Initialize SSH client
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(ip, username=username, password=password)
            self.sftp_client = self.client.open_sftp()
            self.logger.info(f"Connected to {ip}")
        except Exception as e:
            self.logger.error(f"Failed to connect to {ip}: {e}")
            raise

    def copy_file(self, src_file: str, dst_file: str):
        """
        Copies a file to the remote server.

        :param src_file: Local source file path.
        :param dst_file: Destination path on the server.
        """
        try:
            self.logger.info(f"Copying {src_file} to {dst_file}")
            self.sftp_client.put(src_file, dst_file)
            self.logger.info(f"Successfully copied {src_file} to {dst_file}")
        except Exception as e:
            self.logger.error(f"Failed to copy {src_file} to {dst_file}: {e}")

    def create_dir_sftp(self, path: str):
        """
        Creates a directory on the remote server via SFTP.

        :param path: Directory path to create.
        """
        try:
            self.sftp_client.stat(path)  # Check if directory exists
        except FileNotFoundError:
            try:
                self.sftp_client.mkdir(path)
                self.logger.info(f"Created directory: {path}")
            except Exception as e:
                self.logger.error(f"Failed to create directory {path}: {e}")

    def get_file_size(self, file_path: str) -> int | str:
        """
        Retrieves the size of a file on the remote server.

        :param file_path: Path to the remote file.

        :return: File size in bytes, or "Does not exist" if the file is missing.
        """
        try:
            return self.sftp_client.stat(file_path).st_size
        except FileNotFoundError:
            self.logger.warning(f"File does not exist: {file_path}")
            return "Does not exist"
        except Exception as e:
            self.logger.error(f"Failed to get file size for {file_path}: {e}")
            return "Error"

    def change_owner(self, file_path: str, owner: str):
        """
        Changes the ownership of a file on the remote server.

        :param file_path: Path to the file.
        :param owner: New owner username.
        """
        try:
            command = f"echo {os.getenv('VM_PASSWORD')} | sudo -S chown {owner}:{owner} {file_path}"
            self.logger.info(f"Changing owner of {file_path} to {owner}")
            self.client.exec_command(command)
            time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Failed to change owner of {file_path}: {e}")

    def find_new_file_name(self, file_path: str) -> str:
        """
        Finds a new backup name for a file by appending `_old` before the extension.

        :param file_path: Original file path.

        :return: New file name with `_old` suffix.
        """
        base, ext = os.path.splitext(file_path)
        new_path = f"{base}_old{ext}"

        while True:
            try:
                self.sftp_client.stat(new_path)  # Check if file already exists
                base, ext = os.path.splitext(new_path)
                new_path = f"{base}_old{ext}"
            except FileNotFoundError:
                return new_path

    def send_file(self, file_path_from: str, file_path_to: str):
        """
        Sends a file to the remote server, making a backup of the existing file if necessary.

        :param file_path_from: Local source file path.
        :param file_path_to: Destination path on the remote server.
        """
        try:
            # Check if destination file exists
            self.sftp_client.stat(file_path_to)
            backup_path = self.find_new_file_name(file_path_to)

            self.logger.info(f"Backing up {file_path_to} to {backup_path}")
            self.client.exec_command(f"echo {os.getenv('VM_PASSWORD')} | sudo -S mv {file_path_to} {backup_path}")
            time.sleep(0.1)

            self.logger.info(f"Copying {file_path_from} to {file_path_to}")
            self.sftp_client.put(file_path_from, file_path_to)
        except FileNotFoundError:
            self.logger.info(f"No existing file at {file_path_to}, copying directly.")
            self.sftp_client.put(file_path_from, file_path_to)
        except Exception as e:
            self.logger.error(f"Failed to send file {file_path_from} to {file_path_to}: {e}")

    def set_info(self, info: FileInfo):
        """
        Sets metadata information.

        :param info: A FileInfo object containing file metadata.
        """
        self.info = info

    def get_info(self) -> FileInfo | None:
        """
        Retrieves stored file metadata.

        :return: A FileInfo object or None if not set.
        """
        return self.info

    def close(self):
        """
        Closes the SSH and SFTP connections.
        """
        self.sftp_client.close()
        self.client.close()
        self.logger.info(f"Closed SSH connection to {self.ip}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
