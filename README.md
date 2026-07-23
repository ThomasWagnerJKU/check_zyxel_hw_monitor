# check_Zyxel_HW_monitor
This projects contains plugins for monitoring Zyxel devices using SNMP. The plugins are compatible with Nagios, Icinga, and other monitoring systems that support Nagios plugins.

Zyxel devices are supported by the following MIBs:
<https://mibs.observium.org/mib/ZYXEL-HW-MONITOR-MIB/>
<https://mibs.observium.org/mib/ZYXEL-ES-COMMON/>

## Included checks

- `check_zyxel-cpu`: CPU usage (%)
- `check_zyxel-mem`: memory usage (%)
- `check_zyxel-flash`: flash usage (%)
- `check_zyxel-fan`: fan RPM (indexed sensor)
- `check_zyxel-temperature`: temperature (indexed sensor)
- `check_zyxel-voltage`: voltage (indexed sensor)
- `check_zyxel-power`: power source status (indexed source)
- `check_zyxel-time`: switch time skew against an NTP server or local machine time

All scripts use `snmpget`, return Nagios-compatible exit codes, and print performance data where available.

## SNMP authentication

### SNMPv2c

Use `-H` for host and `-C` for community:

```bash
./check_zyxel-cpu -H 192.168.1.1 -C public -w 80 -c 90
./check_zyxel-temperature -H 192.168.1.1 -C public -i 1 -w 70 -c 80
./check_zyxel-time -H 192.168.1.1 -N pool.ntp.org -C public -w 5 -c 30
./check_zyxel-flash -H 192.168.1.1 -C public -o .1.3.6.1.4.1.x.x.x.0 -w 80 -c 90
```

### SNMPv3

Use `-V 3` and pass user/security credentials:

```bash
./check_zyxel-cpu -H 192.168.1.1 -V 3 -u monitor -l authPriv -a SHA -A authpass -x AES -X privpass -w 80 -c 90
./check_zyxel-power -H 192.168.1.1 -V 3 -u monitor -l authNoPriv -a SHA -A authpass -i 1
./check_zyxel-time -H 192.168.1.1 -N pool.ntp.org -V 3 -u monitor -l authPriv -a SHA -A authpass -x AES -X privpass -w 5 -c 30
```

## Notes

- Scripts use numeric OIDs and do not require MIB files on the target test system.
- For indexed sensors (`fan`, `temperature`, `voltage`, `power`), use `-i` to select the sensor/source index.
- `check_zyxel-time` requires one of: `ntpdate`, `sntp`, or `python3` to query the given NTP server.
- If `-N` is omitted for `check_zyxel-time`, the script compares switch time against local machine time.
- `check_zyxel-flash` uses `.1.3.6.1.4.1.890.1.15.3.2.6.0` by default; some models do not implement this OID. Use `-o` to provide a model-specific flash usage OID.
