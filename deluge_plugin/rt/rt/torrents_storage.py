from collections import namedtuple


class TorrentsStorage():

	stored_torrents = []
	stored_files = {}
	active_requests = {}

	def __init__(self, core):
		self.core = core
		self.update_torrent_list()

	def update_torrent_list(self):
		torrent_ids = self.core.get_session_state()
		for torrent_id in torrent_ids:
			if torrent_id not in self.stored_torrents:
				self.add_torrent(torrent_id)

	def add_torrent(self, torrent_id):
		self.stored_torrents.append(torrent_id)
		status = self.core.torrentmanager[torrent_id].get_status(["save_path"])
		files = self.core.torrentmanager[torrent_id].get_files()
		for file in files:
			self.add_file(torrent_id, status["save_path"], file)

	def add_file(self, torrent_id, torrent_path, file):
		self.stored_files[torrent_path + '/' + file["path"]] = {"torrent_id": torrent_id, "offset": file["offset"]}
		print "Path: " + torrent_path + '/' + file["path"]
		print "Torrent id: " + torrent_id
		print "Offset: " + str(file["offset"])

	def exists(self, path):
		if path in self.stored_files:
			return True
		self.update_torrent_list()
		return path in self.stored_files

	def get_torrent_offset(self, path, file_offset):
		if self.exists(path):
			return self.stored_files[path]["offset"] + file_offset
		else
			return -1

	def get_torrent_piece_idx(self, path, file_offset):
		torrent_offset = self.get_torrent_offset(self, path, file_offset)
		if torrent_offset == -1:
			return -1
		torrent_id = self.stored_files[path]["torrent_id"]
		torrent = self.core.torrentmanager[torrent_id]
		return torrent_offset / torrent.get_status(["piece_length"])["piece_length"]

	def prioritize_piece(self, torrent_id, piece_idx):
		torrent_handle = self.core.torrentmanager[torrent_id].handle
		handle.set_piece_deadline(piece_idx, 0)

	def response_to_all_ready(self):
		session = self.core.session()
		