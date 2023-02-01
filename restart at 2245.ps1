$h = 22
$m = 45
$d = 0 #today: 0, tomorrow: 1
$date = (get-date -Hour $h -Minute $m -Second 0).AddDays($d)
$host.ui.RawUI.WindowTitle = "restart at " + $date.tostring("HH:mm")
write-warning "Will restart at $date"
start-sleep ($date - (get-date)).totalseconds
restart-Computer -Force