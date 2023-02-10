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

function Get-MDHRuValue {
    param(
        [Parameter(Mandatory)]$username,
        [Parameter(Mandatory)]$password,
        [Parameter(Mandatory)]$uri
        [Parameter(Mandatory)]$ticker,
        [Parameter(Mandatory)]$field,
        [Parameter(Mandatory)]$from,
        [Parameter(Mandatory)]$to
    )
    $pwd = ConvertTo-SecureString $password -AsPlainText -Force
    $cred = New-Object Management.Automation.PSCredential($username, $pwd)
    $params = @{
        Authentication = "Basic"
        Credential = $cred
        Uri = "$uri/$ticker/data/?field=$field&from=$from&to=$to"
    }
    $response = Invoke-WebRequest @param
    if ($response.StatusCode -ne 200) {
        Write-Warning "Failed with status: $($response.StatusDescription)"
        return $false
    }
    try { $responseJson = $response.Content | ConvertFrom-Json }
    catch {
        Write-Warning "Failed to parse response"
        return $false
        }
    return $true,$responseJson
}