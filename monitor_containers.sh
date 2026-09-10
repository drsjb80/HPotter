#!/bin/bash
# Monitor Docker container growth over time
# Run this in another terminal to track container accumulation

echo "Container Monitoring Script - HPotter Cleanup Verification"
echo "==========================================================="
echo ""
echo "This script monitors container growth. If cleanup is working:"
echo "  - Total container count should remain stable (or grow very slowly)"
echo "  - New containers should appear and disappear quickly"
echo "  - No containers should persist for hours/days"
echo ""
echo "Start time: $(date)"
echo ""

INTERVAL=${1:-30}  # Default 30 seconds between checks
echo "Checking every $INTERVAL seconds (pass different value to change)"
echo ""

# Initial count
get_counts() {
    TOTAL=$(docker ps -a -q | wc -l)
    RUNNING=$(docker ps -q | wc -l)
    STOPPED=$(( TOTAL - RUNNING ))
}

# Print header
printf "%-20s %-10s %-10s %-15s\n" "Time" "Total" "Running" "Stopped"
printf "%-20s %-10s %-10s %-15s\n" "----" "-----" "-------" "-------"

PREV_TOTAL=0
get_counts
printf "%-20s %-10s %-10s %-15s\n" "$(date '+%H:%M:%S')" "$TOTAL" "$RUNNING" "$STOPPED"
PREV_TOTAL=$TOTAL

# Monitor loop
while true; do
    sleep $INTERVAL
    get_counts

    DELTA=$(( TOTAL - PREV_TOTAL ))
    DELTA_STR=""
    if [ $DELTA -gt 0 ]; then
        DELTA_STR=" (+$DELTA)"
    elif [ $DELTA -lt 0 ]; then
        DELTA_STR=" ($DELTA)"
    fi

    printf "%-20s %-10s %-10s %-15s%s\n" "$(date '+%H:%M:%S')" "$TOTAL" "$RUNNING" "$STOPPED" "$DELTA_STR"
    PREV_TOTAL=$TOTAL
done
