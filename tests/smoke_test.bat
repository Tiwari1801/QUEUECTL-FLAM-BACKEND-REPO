@echo off
setlocal enabledelayedexpansion

echo == Enqueuing jobs ==
python queuectl.py enqueue "{\"id\":\"job1\",\"command\":\"echo Hello World\",\"max_retries\":3}"
python queuectl.py enqueue "{\"id\":\"job2\",\"command\":\"bash -c 'exit 1'\",\"max_retries\":2}"

echo == Starting worker ==
start /b python -u queuectl.py worker start --count 1
timeout /t 5 /nobreak >nul

echo == Status after 5s ==
python queuectl.py status

timeout /t 10 /nobreak >nul
echo == Listing DLQ ==
python queuectl.py dlq-list

echo == Retrying DLQ jobs ==
python queuectl.py dlq-retry job2

timeout /t 3 /nobreak >nul
echo == Final status ==
python queuectl.py status

echo == Done ==
endlocal
pause
