import ui
from objc_util import *


LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace')
defaultWorkspace = LSApplicationWorkspace.defaultWorkspace()

class LauncherView(ui.View):
	def __init__(self, itemsDicts, width=512, height=512):
		self.width, self.height = (width, height)
		self.mainTable = ui.TableView()
		self.mainTable.data_source = MainTableDataSource(itemsDicts)
		self.mainTable.delegate = MainTableDelegate()
		self.mainTable.width = self.width
		self.mainTable.height = self.height
		self.add_subview(self.mainTable)


class MainTableDataSource (object):
	def __init__(self, appDicts):
		self.userApps = sorted(appDicts[0], key=lambda x: x['name'])
		self.systemApps = sorted(appDicts[1], key=lambda x: x['name'])
		
	def tableview_number_of_sections(self, tableview):
		# Return the number of sections (defaults to 1)
		return 2

	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		if section is 0:
			return len(self.userApps)
		elif section is 1:
			return len(self.systemApps)

	def tableview_cell_for_row(self, tableview, section, row):
		# Create and return a cell for the given section/row
		cell = ui.TableViewCell()
		if section is 0:
			cell.text_label.text = self.userApps[row]['name']
			cell.image_view.image = self.userApps[row]['icon']
			cell.id = self.userApps[row]['id']
		elif section is 1:
			cell.text_label.text = self.systemApps[row]['name']
			cell.image_view.image = self.systemApps[row]['icon']
			cell.id = self.systemApps[row]['id']
		return cell

	def tableview_title_for_header(self, tableview, section):
		# Return a title for the given section.
		# If this is not implemented, no section headers will be shown.
		if section is 0:
			return 'User Apps'
		elif section is 1:
			return 'System Apps'

	def tableview_can_delete(self, tableview, section, row):
		# Return True if the user should be able to delete the given row.
		return False

	def tableview_can_move(self, tableview, section, row):
		# Return True if a reordering control should be shown for the given row (in editing mode).
		return False

class MainTableDelegate (object):
	def tableview_did_select(self, tableview, section, row):
		# Called when a row was selected.
		if section is 0:
			id = tableview.data_source.userApps[row]['id']		
		elif section is 1:
			id = tableview.data_source.systemApps[row]['id']

		defaultWorkspace.openApplicationWithBundleID_(id)

def createLists():
	userAppList = []
	systemAppList = []
	userApps = defaultWorkspace.applicationsOfType_(0)
	systemApps = defaultWorkspace.applicationsOfType_(1)
	
	for userApp in userApps:
		userAppList.append({
			'name': str(userApp.localizedName()),
			'icon': ui.Image.from_data(uiimage_to_png(UIImage._applicationIconImageForBundleIdentifier_format_scale_(userApp.bundleIdentifier(), 1, 100))),
			'id': str(userApp.bundleIdentifier())
		})
	for systemApp in systemApps:
		if 'hidden' in str(systemApp.appTags()): continue
		exclude = ['Web', 'WebApp1', 'HashtagImages']
		if str(systemApp.localizedName()) in exclude: continue
		systemAppList.append({
			'name': str(systemApp.localizedName()),
			'icon': ui.Image.from_data(uiimage_to_png(UIImage._applicationIconImageForBundleIdentifier_format_scale_(systemApp.bundleIdentifier(), 1, 100))),
			'id': str(systemApp.bundleIdentifier())
		})
	return [userAppList, systemAppList]

appDicts = createLists()
size = max(ui.get_window_size()/2)
launcher = LauncherView(appDicts, size, size)
launcher.present('sheet')
