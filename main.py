#!/usr/bin/env python3

# TODO
# --Quality selection combobox bottom mid
# --Watch button bottom left
# --JSON saving more than URLs
# --Save window size
# --Edit entries
# Ordered save urls
# Aliases
# Stream error handling, statusbar maybe?
#    no stream in selected quality, etc
# Hosting someone else's stream?
# User selectable media player
# Menubar File->Add,Open,Reload,Exit;View->messages.log,Preferences,About
# Preferences check_if_online on startup, media player path, hide url domain


import os, sys
import json

#~ from PySide.QtGui import QApplication, QLabel, QPushButton, QLineEdit, QWidget, QTextEdit, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu
from PySide.QtGui import *
from PySide.QtCore import Qt

from stream import *

# changes relative into full path so we can run from anywhere
def fullpath( relpath ):
	return os.path.join(os.path.dirname(__file__), relpath)

	# FileNotFoundError is python3.3+ only
try:
	TryFileNotFound = FileNotFoundError
except NameError:
	TryFileNotFound = IOError


class LiveStreamer( QWidget ):

	def __init__( self ):
		super(LiveStreamer, self).__init__()

		messages = QTextEdit()
		messagesLabel = QLabel( 'Messages' )
		links = QTableWidget( 0, 2 )
		clearMessages = QPushButton( 'Clear Messages' )
		checkIfOnline = QPushButton( QIcon( QPixmap( fullpath( 'icons/reload_16.png' ) ) ), '' )
		addLink = QPushButton( QIcon( QPixmap( fullpath( 'icons/add_16.png' ) ) ), '' )
		watchButton = QPushButton( QIcon( QPixmap( fullpath( 'icons/play_16.png' ) ) ), 'Watch' )

		self.qualityComboBox = QComboBox()
		#~ qualityComboBox.setEditable(True)
		self.qualityComboBox.addItems('Best High Medium Low Mobile Audio'.split())
		self.qualityComboBox.currentIndexChanged['QString'].connect(self.handle_quality_change)

			# make it pretty
		links.horizontalHeader().hide()
		links.verticalHeader().hide()
		links.setShowGrid(False)
		links.setSelectionBehavior(QAbstractItemView.SelectRows)
		checkIfOnline.setMaximumWidth(32)
		addLink.setMaximumWidth(32)
		width = watchButton.fontMetrics().boundingRect('Watch').width() + 32
		watchButton.setMaximumWidth(width)

			# add right click context menu
		links.setContextMenuPolicy(Qt.CustomContextMenu)
		links.customContextMenuRequested.connect(self.links_context_menu)

		messages.setReadOnly( True )

		links.setHorizontalHeaderLabels( [ 'Status', 'Url' ] )
		links.horizontalHeader().setResizeMode( 0, QHeaderView.ResizeToContents )
		links.horizontalHeader().setResizeMode( 1, QHeaderView.Stretch )

			# set the events
		links.itemDoubleClicked.connect( self.select_stream_from_link )
		clearMessages.clicked.connect( self.clear_messages )
		checkIfOnline.clicked.connect( self.check_if_online )
		addLink.clicked.connect( self.add_link_dialog )
		watchButton.clicked.connect( self.watch_button_handler )

			# set the layouts
		mainLayout = QGridLayout()

			# first row  (links widget occupies 3 rows and 3 columns)
		mainLayout.addWidget( links, 0, 0, 3, 4 )   # spans 3 columns

			# fourth row
		mainLayout.addWidget( watchButton, 3, 0 )
		mainLayout.addWidget( self.qualityComboBox, 3, 1 )
		mainLayout.addWidget( checkIfOnline, 3, 2 )
		mainLayout.addWidget( addLink, 3, 3 )

		window = QWidget()

		window.setLayout( mainLayout )
		window.setWindowTitle( 'Live Streamer' )
		#~ window.resize( 400, 350 )
		window.show()

		self.messages_ui = messages
		self.links_ui = links
		self.window_ui = window

		self.links = set()


	def handle_quality_change( self, text ):
		pass  # don't think we need this yet


	def watch_button_handler( self ):
		self.select_stream_from_link( self.links_ui.currentItem() )


	def links_context_menu( self, pos ):

		menu = QMenu()
		playAction = menu.addAction( QIcon( QPixmap( fullpath( 'icons/play_16.png' ) ) ), "Watch" )
		reloadAction = menu.addAction( QIcon( QPixmap( fullpath( 'icons/reload_16.png' ) ) ), "Reload" )
		editAction = menu.addAction( "Edit" )
		removeAction = menu.addAction( QIcon( QPixmap( fullpath( 'icons/remove_16.png' ) ) ), "Remove" )
		action = menu.exec_( self.links_ui.mapToGlobal( pos ) )
		if action == playAction:
			self.select_stream_from_link( self.links_ui.currentItem() )
		elif action == reloadAction:
			self.reload_selected_link()
		elif action == editAction:
			self.edit_selected_link()
			#~ self.reload_selected_link()
		elif action == removeAction:
			self.remove_selected_link()


	def add_link_dialog( self ):

		text, ok = QInputDialog.getText( self, 'Add Link', 'URL:' )

		if ok:
			self.add_link( text )


	def select_stream_from_link( self, tableWidgetItem ):

		row = tableWidgetItem.row()
		urlItem = self.links_ui.item( row, 1 )  # the url is in the first column
		url = urlItem.text()
		quality = self.qualityComboBox.currentText()
		self.messages_ui.append( 'Trying to open stream: {}'.format( url ) )
		print( 'Trying to open stream: {}'.format( url ) )

		stream = Stream( [url, quality] )
		stream.start( self.messages_ui )


	def clear_messages( self ):

		self.messages_ui.setText( '' )


	def add_link( self, url ):

		"""
			Adds a link to the link widget.

			Only adds if its not already present.
		"""

		if url not in self.links:
			quality = self.qualityComboBox.currentText()

			self.links.add( url )

			rowCounts = self.links_ui.rowCount()
			nextRow = rowCounts + 1
			nextPosition = rowCounts    # row count is the length, but position is zero-based

			self.links_ui.setRowCount( nextRow )

			urlEntry = QTableWidgetItem( url )
			statusEntry = QTableWidgetItem( '' )

			statusEntry.setFlags( statusEntry.flags() & ~Qt.ItemIsEditable ) # not editable
			urlEntry.setFlags( urlEntry.flags() & ~Qt.ItemIsEditable ) # not editable

			self.links_ui.setItem( nextPosition, 0, statusEntry )
			self.links_ui.setCellWidget( nextPosition, 0, ImageWidget( fullpath( 'icons/gray_status_16.png' ), self.links_ui ) )
			self.links_ui.setItem( nextPosition, 1, urlEntry )

				# check if online
			stream = Stream( [url, quality] )
			stream.is_online( statusEntry )


	def edit_selected_link( self ):

		selectedItem = self.links_ui.currentItem()
		if selectedItem:
			newUrl, ok = QInputDialog.getText( self, 'Edit Link', 'URL:', text = selectedItem.text() )

			if ok:
				selectedItem.setText( newUrl )
				self.links_ui.setCellWidget( selectedItem.row(), 0, ImageWidget( fullpath( 'icons/gray_status_16.png' ), self.links_ui ) )


	def remove_selected_link( self ):

		selectedItem = self.links_ui.currentItem()
		if selectedItem:
			self.links.remove( selectedItem.text() )
			currentRow = self.links_ui.currentRow()
			self.links_ui.removeRow( currentRow )


	def reload_selected_link( self ):

		statusItem = self.links_ui.item( self.links_ui.currentRow(), 0 )
		urlItem = self.links_ui.item( self.links_ui.currentRow(), 1 )

		url = urlItem.text()
		quality = self.qualityComboBox.currentText()
		stream = Stream( [url, quality] )

		stream.is_online( statusItem )


	def check_if_online( self ):

		"""
			Check if any of the streams saved is online
		"""

		for row in range( self.links_ui.rowCount() ):

			statusItem = self.links_ui.item( row, 0 )
			urlItem = self.links_ui.item( row, 1 )

			url = urlItem.text()
			quality = self.qualityComboBox.currentText()
			stream = Stream( [url, quality] )
			stream.is_online( statusItem )


	def save( self ):

		"""
			Save any data to a file (the links/etc)
		"""

			# json doesn't have sets, so convert to a list
		linksList = list( self.links )
		saveJsonText = json.dumps( {
			'quality': self.qualityComboBox.currentText(),
			'resHeight': self.window_ui.height(),
			'resWidth': self.window_ui.width(),
			'urls': linksList
		}, sort_keys=True )

		with open( fullpath( 'data.txt' ), 'w', encoding= 'utf-8' ) as f:
			f.write( saveJsonText )


	def load( self ):

		"""
			Load any saved data
		"""

		try:
			file = open( fullpath( 'data.txt' ), 'r', encoding= 'utf-8' )
		except TryFileNotFound:
			return

		data = json.loads( file.read() )
		linksList = data['urls']

		try:
			quality = data['quality']
		except KeyError:
			quality = "Best"

		try:
			resWidth = data['resWidth']
			resHeight = data['resHeight']
		except KeyError:
			resWidth = 300
			resHeight = 350

		file.close()

		self.qualityComboBox.setCurrentIndex( self.qualityComboBox.findText( quality ) )
		for link in linksList:
			self.add_link( link )

		self.window_ui.resize( resWidth, resHeight )

		#~ self.check_if_online()


if __name__ == '__main__':

	app = QApplication( sys.argv )
	streamer = LiveStreamer()
	streamer.load()
	app.aboutToQuit.connect( streamer.save )
	app.exec_()

