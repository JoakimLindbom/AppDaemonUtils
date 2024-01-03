#dest='/mnt/ha/config/appdaemon'
dest='/mnt/ha/addon_configs/a0d7b954_appdaemon/'


cd apps

for f in *
do
   if [ "$f" != 'test' ] && [ "$f" != 'venv' ] && [ "$f" != 'copy.sh' ] && [ "$f" != 'apps2.yaml' ] && [ "$f" != '__pycache__' ] && [ "$f" != 'old' ]; then
     echo "Copying $f "
     sudo cp  "$f" "$dest/apps/$f"
  fi
done

cd ../dashboards

for f in *
do
   if [ "$f" != 'test' ] && [ "$f" != 'venv' ] && [ "$f" != 'copy.sh' ]; then
     echo "Copying $f "
     sudo cp -r "$f" "$dest/dashboards/$f"
  fi
done

cd ..
