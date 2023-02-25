function Send-TelegramMessage{
    param(
      [Parameter(Mandatory)]$chatId,
      [Parameter(Mandatory)]$tgToken,
      [Parameter(Mandatory)]$text
      )
    $URL = "https://api.telegram.org/bot$tgToken/sendMessage"
    $ht = @{
        text = $text
        parse_mode = "HTML"
        chat_id = $chatID
        }
    $json = $ht | ConvertTo-Json
    $e = $true
    while ($e){
        $e = $false
        Write-Host "sending message..."
        try {Invoke-RestMethod $URL -Method Post -ContentType 'application/json; charset=utf-8' -Body $json | Out-Null}
        catch {write-warning "failed! retry in five seconds" ; $e = $true ; Start-Sleep 5}
        }
    }