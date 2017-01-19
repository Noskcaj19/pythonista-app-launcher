from objc_util import *
import sys
import console

LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace')
defaultWorkspace = LSApplicationWorkspace.defaultWorkspace()
def main():
	from ui import Image
	
	USER_APPS = 0
	SYSTEM_APPS = 1
	
	UIImage = ObjCClass('UIImage')

	allApps = defaultWorkspace.applicationsOfType_(USER_APPS)
	
	
	for i, app in enumerate(allApps):
		#print('hidden' in str(app.appTags()))
		console.write_link('{} : {}, version {}. By {}'.format(app.bundleIdentifier(), app.localizedName(), app.shortVersionString(), app.vendorName()), 'pythonista://{}?action=run&argv={}'.format(__file__.rsplit('/Pythonista3/Documents/')[-1], app.bundleIdentifier()))
		Image.from_data(uiimage_to_png(UIImage._applicationIconImageForBundleIdentifier_format_scale_(app.bundleIdentifier(), 1, 100))).show()
		print('\n')


def openApp(id):
	defaultWorkspace.openApplicationWithBundleID_(id)
if __name__ == '__main__':
	if len(sys.argv) == 2:
		openApp(sys.argv[1])
	else:
		main()
