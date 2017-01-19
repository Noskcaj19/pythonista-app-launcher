import ui
import math
from objc_util import *

LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace')
defaultWorkspace = LSApplicationWorkspace.defaultWorkspace()

def createList(items_per_row):
	app_list = []
	user_apps = defaultWorkspace.applicationsOfType_(0)
	system_apps = defaultWorkspace.applicationsOfType_(1)
	
	for user_app in user_apps:
		app_list.append({
			'name': str(user_app.localizedName()),
			'icon': ui.Image.from_data(uiimage_to_png(UIImage._applicationIconImageForBundleIdentifier_format_scale_(user_app.bundleIdentifier(), 1, 100))),
			'id': str(user_app.bundleIdentifier()),
			'type': 'user'
		})
	for system_app in system_apps:
		localizedName = str(system_app.localizedName())
		# Gets rid of the (many) internal apple apps, most of which won't open, skips fieldtest
		if 'hidden' in str(system_app.appTags()) and not str(system_app.bundleIdentifier()) == 'com.apple.fieldtest': continue
		exclude = ['Web', 'WebApp1', 'HashtagImages']
		if localizedName in exclude: continue
		app_list.append({
			'name': localizedName,
			'icon': ui.Image.from_data(uiimage_to_png(UIImage._applicationIconImageForBundleIdentifier_format_scale_(system_app.bundleIdentifier(), 1, 100))),
			'id': str(system_app.bundleIdentifier()),
			'type': 'system'
		})
	# sort alphabetically
	sort1 = sorted(app_list, key=lambda x: x['name'])

	# sort by type (type happened to be in wrong alphebetical order)
	sort2 = sorted(sort1, key=lambda x: x['type'], reverse=True)
	
	# Create padding because i am not sure how to add headers
	last_item = None
	for index, item in enumerate(sort2):
		try:
			if last_item['type'] == 'user' and item['type'] == 'system':
				items_to_add = max(-((index % items_per_row)-5), 0) + items_per_row
				for x in range(items_to_add):
					sort2.insert(index, {'id': None, 'name': '', 'icon': None, 'type': None})
		except TypeError:
			pass
		last_item = item
	
	return sort2


class GridView (ui.View):
	def __init__(self, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		self.visible_range = []
		self.visible_views = {}
		self.items = []
		self.reusable_cells = []
		self.item_size = (120, 120)
		self.scrollview = ui.ScrollView(frame=self.bounds, flex='WH')
		self.scrollview.content_size = (0, 2000)
		self.scrollview.delegate = self
		self.data_source = None
		self.add_subview(self.scrollview)
		
	def reload(self):
		self.visible_range = []
		for v in list(self.visible_views.values()):
			self.scrollview.remove_subview(v)
		self.visible_views = {}
		_, _, w, h = self.bounds
		items_per_row = int(w / self.item_size[0])
		num_rows = math.ceil(len(self.items) / float(items_per_row))
		self.scrollview.content_size = (0, num_rows * self.item_size[1])
		self.scrollview_did_scroll(self.scrollview)
		
	def layout(self):
		self.reload()
		
	def frame_for_item(self, item_index):
		_, _, w, h = self.bounds
		items_per_row = int(w / self.item_size[0])
		row = item_index // items_per_row
		col = item_index % items_per_row
		x_spacing = (w - (items_per_row * self.item_size[0])) / (items_per_row-1)
		return (col*(self.item_size[0] + x_spacing), row*self.item_size[1], self.item_size[0], self.item_size[1])
		
	def create_or_reuse_cell(self):
		if self.reusable_cells:
			cell = self.reusable_cells[0]
			del self.reusable_cells[0]
			return cell
		if self.data_source:
			return self.data_source.gridview_create_cell(self)
		else:
			return ui.View(bg_color='gray')
			
	def configure_cell(self, cell_view, item):
		if self.data_source:
			self.data_source.gridview_configure_cell(self, cell_view, item)
			
	def scrollview_did_scroll(self, scrollview):
		y = scrollview.content_offset[1]
		_, _, w, h = self.bounds
		items_per_row = int(w / self.item_size[0])
		first_visible_row = max(0, int(y / self.item_size[1]))
		num_visible_rows = int(h / self.item_size[1]) + 2
		range_start = first_visible_row * items_per_row
		range_end = min(len(self.items), range_start + num_visible_rows * items_per_row)
		visible_range = range(range_start, range_end)
		if visible_range != self.visible_range:
			self.visible_range = visible_range
			# Remove views that are no longer visible:
			for i in list(self.visible_views.keys()):
				if i not in visible_range:
					cell = self.visible_views[i]
					self.reusable_cells.append(cell)
					self.scrollview.remove_subview(cell)
					del self.visible_views[i]
			# Add views that are not visible yet:
			for i in visible_range:
				if i not in self.visible_views:
					cell_frame = self.frame_for_item(i)
					view = self.create_or_reuse_cell()
					view.frame = cell_frame
					self.configure_cell(view, self.items[i])
					self.scrollview.add_subview(view)
					self.visible_views[i] = view
					
					
class GridViewDemoController (object):
	def __init__(self,):
		self.gridview = GridView(frame=(0, 0, 500, 500), background_color='white', name='GridView Demo')
		self.gridview.item_size = (100, 120)
		self.gridview.data_source = self
		_, _, w, h = self.gridview.bounds
		items_per_row = int(w / self.gridview.item_size[0])
		self.appDict = createList(items_per_row)
		self.gridview.items = self.appDict
		
	# Data source methods:
	def gridview_create_cell(self, gridview):
		cell = ui.View(frame=(0, 0, 100, 100))
		app = ui.Button(frame=(10, 10, 80, 60), name='app', flex='wh')
		app.corner_radius = 4
		app.action = self.app_pressed
		cell.add_subview(app)
		label = ui.Label(frame=(10, 80, 80, 15), name='label', flex='wt')
		label.font = ('<System>', 13)
		label.alignment = ui.ALIGN_CENTER
		label.text_color = '#333333'
		cell.add_subview(label)
		cell.id = None
		return cell
	
	def app_pressed(self, sender):
		print(sender.superview.id)
		defaultWorkspace.openApplicationWithBundleID_(sender.superview.id)

	def gridview_configure_cell(self, gridview, cell, item):
		cell['label'].text = item['name']
		cell.id = item['id']
		cell['app'].background_image = item['icon']
		
demo = GridViewDemoController()
demo.gridview.present('sheet')
