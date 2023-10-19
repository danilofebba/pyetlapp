cd ~/Documents
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install --upgrade jupyterlab
jupyter lab --generate-config
echo -e "c.NotebookApp.token = ''" >> ~/.jupyter/jupyter_lab_config.py
echo -e "c.NotebookApp.password = 'argon2:\$argon2id\$v=19\$m=10240,t=10,p=8\$635AifC1hEtV+BPmOyHphQ\$lP1zV4+cd0BODPyv3IW7h4j/3PKd8cnAgJGoebpsqwA'" >> ~/.jupyter/jupyter_lab_config.py
python3 -m pip install --upgrade numpy pyarrow pandas
python3 -m pip install --upgrade pyspark
python3 -m pip install --upgrade "psycopg[binary]"
#jupyter lab --ip=0.0.0.0 --allow-root
