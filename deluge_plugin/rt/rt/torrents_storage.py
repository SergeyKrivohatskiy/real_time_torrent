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
			return -1, -1
		torrent_id = self.stored_files[path]["torrent_id"]
		torrent = self.core.torrentmanager[torrent_id]
		piece_len = torrent.get_status(["piece_length"])["piece_length"]
		piece_idx = torrent_offset / piece_len
		len_to_end = piece_idx * piece_length - torrent_offset
		return piece_idx, len_to_end


	def prioritize_piece(self, torrent_id, piece_idx):
		prioritize_piece_count = 5
		handle = self.core.torrentmanager[torrent_id].handle
		handle.set_piece_priority(piece_idx, 3)
		for i in range(piece_idx + 1, piece_idx + prioritize_piece_count + 1):
			if handle.get_piece_priority(piece_idx) == 3:
				continue
			handle.set_piece_priority(piece_idx, 2)

	def is_loaded(self, torrent_id, piece_idx):
		handle = self.core.torrentmanager[piece_id.torrent_id].handle
		if !handle.have_piece(piece_id.piece_idx):
			return False
		session = self.core.session
		hsh = bytes(handle.info_hash().to_string())
		cached = session.get_cache_info(hsh)
		for item in cached:
			if item.piece == piece_id.piece_idx && item.kind == 1:
				handle.flush_cache()
				return False
		return True

	def on_request(self, offset, path, timeout, req_id, on_response):
