#!/bin/bash

if command -v kaggle > /dev/null;then
  echo "kaggle is installed"
else
  pip install kaggle
fi

mkdir -p ~/.kaggle data/
if [ ! -f ~/.kaggle/kaggle.json ];then
  opt=$(find . -name "kaggle.json")
  if [ -z $opt ];then
    echo 'download kaggle.json file from the settings of your profile on Kaggle website and run this bash shell again'
  else
    mv $opt ~/.kaggle/kaggle.json
  fi
fi

kaggle competitions download -c favorita-grocery-sales-forecasting --path data
files=$(ls data/)
unzip data/$files -d data/
rm data/$files
for f in data/*.7z;do
  7z x "$f" -o"data/" > /dev/null && rm -f "$f"
done
ls -a data