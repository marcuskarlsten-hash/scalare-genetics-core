import unittest, tempfile, os
from pathlib import Path
class DesktopSmoke(unittest.TestCase):
 def test_window_and_navigation(self):
  from desktop import Desktop,core
  with tempfile.TemporaryDirectory() as d:
   old=core.DB; core.DB=Path(d)/'test.sqlite3'
   try:
    with core.db() as c:c.executescript('CREATE TABLE records(uid INTEGER,kind TEXT,id TEXT,data TEXT,PRIMARY KEY(uid,kind,id)); CREATE TABLE photos(uid INTEGER,fish TEXT,id TEXT,mime TEXT,blob BLOB,PRIMARY KEY(uid,id));')
    win=Desktop()
    try:
     win.update();win.uid=1;win.home();win.update();win.edit('fish');win.update();win.simulator();win.update();win.advice();win.update();win.target_ui();win.update();win.test_cross_ui();win.update();win.generation_ui();win.update();win.visual_ui();win.update();win.intelligence_ui();win.update();win.integrated_ui();win.update();win.pathway_ui();win.update()
    finally:win.destroy()
   finally:core.DB=old
if __name__=='__main__':unittest.main()
