Automatic run while systerm start
```bash
sudo chmod +x ulord.sh
sudo mv ulord.sh /etc/init.d/
cd /etc/init.d/
sudo update-rc.d ulord.sh defaults 90
```
remove automatic run
```
sudo update-rc.d -f ulord.sh remove
```