# PowerShell script to test the Swiss Transport API

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Testing Swiss Transport API" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Home coordinates
$latitude = 47.41729671900619
$longitude = 9.357221339051806

Write-Host "TEST 1: Find Nearest Station" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow
Write-Host "Coordinates: $latitude, $longitude"
Write-Host ""

# Test finding nearest station
$locUrl = "http://transport.opendata.ch/v1/locations?x=$latitude&y=$longitude" + "&type=station"
Write-Host "Request: GET $locUrl" -ForegroundColor Gray

try {
    $locResponse = Invoke-RestMethod -Uri $locUrl -Method Get
    
    $stations = $locResponse.stations
    Write-Host "Success: Stations found: $($stations.Count)" -ForegroundColor Green
    
    # Filter for stations with valid IDs (some results have null IDs)
    $validStations = $stations | Where-Object { $_.id -ne $null -and $_.id -ne "" }
    Write-Host "Valid stations with IDs: $($validStations.Count)" -ForegroundColor Cyan
    
    if ($validStations.Count -gt 0) {
        $nearestStation = $validStations[0]
        Write-Host ""
        Write-Host "Nearest Station:" -ForegroundColor Cyan
        Write-Host "  Name: $($nearestStation.name)" -ForegroundColor White
        Write-Host "  ID: $($nearestStation.id)" -ForegroundColor White
        Write-Host "  Distance: $($nearestStation.distance) meters" -ForegroundColor White
        
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "TEST 2: Get Stationboard" -ForegroundColor Yellow
        Write-Host "----------------------------" -ForegroundColor Yellow
        
        # Get stationboard
        $stationId = $nearestStation.id
        $boardUrl = "http://transport.opendata.ch/v1/stationboard?id=$stationId" + "&limit=10"
        Write-Host "Request: GET $boardUrl" -ForegroundColor Gray
        Write-Host ""
        
        $boardResponse = Invoke-RestMethod -Uri $boardUrl -Method Get
        $connections = $boardResponse.stationboard
        
        Write-Host "Success: Connections found: $($connections.Count)" -ForegroundColor Green
        Write-Host ""
        
        if ($connections.Count -gt 0) {
            Write-Host "First 5 Connections:" -ForegroundColor Cyan
            Write-Host ""
            
            for ($i = 0; $i -lt [Math]::Min(5, $connections.Count); $i++) {
                $conn = $connections[$i]
                $line = "$($conn.category) $($conn.number)"
                $to = $conn.to
                $departure = $conn.stop.departure
                $platform = $conn.stop.platform
                
                Write-Host "  $($i + 1). $line" -ForegroundColor Yellow -NoNewline
                Write-Host " to " -NoNewline
                Write-Host "$to" -ForegroundColor Cyan
                Write-Host "     Departure: $departure" -ForegroundColor White
                Write-Host "     Platform: $platform" -ForegroundColor Gray
                Write-Host ""
            }
            
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host "TEST 3: Timezone Check" -ForegroundColor Yellow
            Write-Host "----------------------------" -ForegroundColor Yellow
            
            # Get current time
            $now = Get-Date
            Write-Host "Current local time: $($now.ToString('yyyy-MM-ddTHH:mm:sszzz'))" -ForegroundColor White
            
            # Parse first connection's departure time
            $firstDeparture = [DateTime]::Parse($connections[0].stop.departure)
            Write-Host "First departure:    $($firstDeparture.ToString('yyyy-MM-ddTHH:mm:sszzz'))" -ForegroundColor White
            
            $timeDiff = ($firstDeparture - $now).TotalMinutes
            $timeDiffRounded = [Math]::Round([Math]::Abs($timeDiff), 1)
            Write-Host ""
            if ($timeDiff -gt 0) {
                Write-Host "Success: First departure is in the future ($timeDiffRounded minutes from now)" -ForegroundColor Green
            } else {
                Write-Host "ERROR: First departure is in the past ($timeDiffRounded minutes ago)" -ForegroundColor Red
                Write-Host "  This might explain why no connections are displayed!" -ForegroundColor Red
            }
            
        } else {
            Write-Host "ERROR: No connections found in stationboard!" -ForegroundColor Red
        }
        
    } else {
        Write-Host "ERROR: No stations found near coordinates!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Tests Complete" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
