function Send-TelegramMessage {
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

function FolderSelector {
    param (
        [Parameter(Mandatory)][string]$Path
    )
    if (Test-Path $Path) {
        $inputFoldersList = Get-ChildItem -Directory -Path $Path
    } else {
        throw "$Path not found"
    }
    if ($inputFoldersList.count -lt 1) {
        throw "No folders in $Path"
    }  
    $count  = 0
    $inputFolders = @{}
    $inputFoldersList | ForEach-Object {
        $count += 1
        $inputFolders.($count) = $_.FullName
    }
    $selection = 0
    while ($selection -notin $inputFolders.keys) {
        Clear-Host
        Write-Warning "No input folder was provided"
        Write-Host "Select folder:"
        $inputFolders.Keys | Sort-Object | ForEach {
            Write-Host "$_`t$($inputFolders.$_)"
        }
        [int]$selection = Read-Host -Prompt "folder number"
    }
    return $inputFolders.$selection
}
