dest='/mnt/ha/config/appdaemon'

cd apps

 echo "Copying $f "
 sudo cp Tester.py "$dest/apps/"
 #sudo cp Button_Controller.py "$dest/apps/"
 sudo cp apps.yaml "$dest/apps/"
 #sudo cp buttonClicked.py "$dest/apps/"

cd ..
