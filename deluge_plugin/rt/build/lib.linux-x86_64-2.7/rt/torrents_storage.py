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
		else:
			return -1

	def get_torrent_piece_info(self, path, file_offset):
		torrent_offset = self.get_torrent_offset(path, file_offset)
		if torrent_offset == -1:
			return -1, -1, -1
		torrent_id = self.stored_files[path]["torrent_id"]
		torrent = self.core.torrentmanager[torrent_id]
		piece_len = torrent.get_status(["piece_length"])["piece_length"]
		piece_idx = torrent_offset / piece_len
		len_to_end = (piece_idx + 1) * piece_len - torrent_offset
		return torrent_id, piece_idx, len_to_end


	def prioritize_piece(self, torrent_id, piece_idx):
		prioritize_piece_count = 5
		handle = self.core.torrentmanager[torrent_id].handle
		handle.piece_priority(piece_idx, 3)
		for i in range(piece_idx + 1, piece_idx + prioritize_piece_count + 1):
			if handle.piece_priority(piece_idx) == 3:
				continue
			handle.piece_priority(piece_idx, 2)

	def is_loaded(self, torrent_id, piece_idx):
		handle = self.core.torrentmanager[torrent_id].handle
		if not handle.have_piece(piece_idx):
			return False
		session = self.core.session
		hsh = bytes(handle.info_hash().to_string())
		cached = session.get_cache_info(hsh)
		for item in cached:
			if item['piece'] == piece_idx and item['kind'] == 1:
				handle.flush_cache()
				return False
		return True

	def on_request(self, offset, path, timeout, req_id, on_response):
		path = path.decode('utf_8')
		timeout = 1000
		#print "Request"
		#print path
		#print offset
		torrent_id, piece_idx, len_to_end = self.get_torrent_piece_info(path, offset)
		if torrent_id == -1:
			on_response(req_id, 12345678)
			print "wrong file"
			return
		self.prioritize_piece(torrent_id, piece_idx)
		if self.is_loaded(torrent_id, piece_idx):
			print len_to_end
			on_response(req_id, len_to_end)
			print "loaded fast"
			return
		from time import sleep
		while timeout > 0:
			sleep(0.1)
			timeout -= 0.1
			if self.is_loaded(torrent_id, piece_idx):
				on_response(req_id, len_to_end)
				print "loaded slow" + str(timeout)
				return
		on_response(req_id, -1)
