# ls: без аргументов, абсолютный путь, относительный путь
ls
ls /
ls docs
ls /docs/reports/2026
# cd: абсолютный, относительный, вверх, без аргументов (в корень)
cd /docs
cd reports
cd 2026
ls
cd ..
cd /home/user
cd
ls
# cat: текстовые и двоичные файлы, относительный путь
cd /home/user
cat settings.conf
cd /
cat /motd
cat docs/readme.txt
cat /docs/reports/2026/q1.txt
cat home/user/bin/logo.bin
# exit: завершение работы
exit