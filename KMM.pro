TEMPLATE = app
TARGET += 
DEPENDPATH += . UI
INCLUDEPATH += .

SOURCES += dbUtils.py \
	   internalwin.py \
	   itemObjects.py \
	   KMM.py \
	   utilities.py \
	   xmlparse.py \
	   UI/ui_addchar.py \
	   UI/ui_assets.py \
	   UI/ui_capitalships.py \
	   UI/ui_mainwindow.py \
	   UI/ui_minstock.py \
	   UI/ui_production.py \
	   UI/ui_production_hist.py \
	   UI/ui_skills.py
RESOURCES += UI/resources.qrc
