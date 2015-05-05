
class TorrentsStorage():

	stored_torrents = []
	stored_files = {}

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
		self.stored_files[torrent_path + file["path"]] = {"torrent_id": torrent_id, "offset": file["offset"]}
		print "Path: " + torrent_path + file["path"]
		print "Torrent id: " + torrent_id
		print "Offset: " + str(file["offset"])
