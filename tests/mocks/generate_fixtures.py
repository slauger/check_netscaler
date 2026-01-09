#!/usr/bin/env python3
"""
Generate fixture JSON files from existing test mocks

This script extracts mock response data from test files and generates
JSON fixture files for the mock NITRO API server.
"""

import base64
import json
from datetime import datetime, timedelta
from pathlib import Path


def generate_fixtures():
    """Generate all fixture files"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    config_dir = fixtures_dir / "config"
    stat_dir = fixtures_dir / "stat"

    print("Generating fixtures...")

    # Service fixtures
    print("  - service (config + stat)")
    service_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "service": [
            {
                "name": "svc_web1",
                "servicetype": "HTTP",
                "ipaddress": "10.1.1.10",
                "port": 80,
                "svrstate": "UP",
                "state": "ENABLED",
                "server": "web1.example.com",
                "maxclient": 0,
                "maxreq": 0,
                "cacheable": "NO",
                "cip": "DISABLED",
                "usip": "NO",
                "sp": "OFF",
                "rtspsessionidremap": "OFF",
                "clttimeout": 180,
                "svrtimeout": 360,
            },
            {
                "name": "svc_web2",
                "servicetype": "HTTP",
                "ipaddress": "10.1.1.11",
                "port": 80,
                "svrstate": "UP",
                "state": "ENABLED",
                "server": "web2.example.com",
                "maxclient": 0,
                "maxreq": 0,
                "cacheable": "NO",
                "cip": "DISABLED",
                "usip": "NO",
                "sp": "OFF",
                "rtspsessionidremap": "OFF",
                "clttimeout": 180,
                "svrtimeout": 360,
            },
            {
                "name": "svc_web_down",
                "servicetype": "HTTP",
                "ipaddress": "10.1.1.12",
                "port": 80,
                "svrstate": "DOWN",
                "state": "ENABLED",
                "server": "web3.example.com",
                "maxclient": 0,
                "maxreq": 0,
                "cacheable": "NO",
                "cip": "DISABLED",
                "usip": "NO",
                "sp": "OFF",
                "rtspsessionidremap": "OFF",
                "clttimeout": 180,
                "svrtimeout": 360,
            },
        ],
    }

    service_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "service": [
            {
                "name": "svc_web1",
                "throughput": 1024,
                "avgsvrttfb": 50,
                "state": "UP",
                "totalrequests": 10000,
                "totalresponses": 10000,
                "totalrequestbytes": 50000000,
                "totalresponsebytes": 100000000,
                "curclntconnections": 5,
                "surgecount": 0,
                "cursrvrconnections": 5,
                "svrestablishedconn": 5,
                "curreusepool": 0,
                "maxclients": 0,
            },
            {
                "name": "svc_web2",
                "throughput": 2048,
                "avgsvrttfb": 45,
                "state": "UP",
                "totalrequests": 15000,
                "totalresponses": 15000,
                "totalrequestbytes": 75000000,
                "totalresponsebytes": 150000000,
                "curclntconnections": 8,
                "surgecount": 0,
                "cursrvrconnections": 8,
                "svrestablishedconn": 8,
                "curreusepool": 0,
                "maxclients": 0,
            },
            {
                "name": "svc_web_down",
                "throughput": 0,
                "avgsvrttfb": 0,
                "state": "DOWN",
                "totalrequests": 0,
                "totalresponses": 0,
                "totalrequestbytes": 0,
                "totalresponsebytes": 0,
                "curclntconnections": 0,
                "surgecount": 0,
                "cursrvrconnections": 0,
                "svrestablishedconn": 0,
                "curreusepool": 0,
                "maxclients": 0,
            },
        ],
    }

    write_fixture(config_dir / "service.json", service_config)
    write_fixture(stat_dir / "service.json", service_stat)

    # ServiceGroup fixtures
    print("  - servicegroup (config + stat)")
    servicegroup_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "servicegroup": {
            "servicegroupname": "sg_web",
            "servicetype": "HTTP",
            "state": "ENABLED",
            "numofconnections": 0,
            "serviceconftype": 1,
            "value": "0",
            "monstate": "ENABLED",
            "maxclient": 0,
            "maxreq": 0,
            "cacheable": "NO",
            "cip": "DISABLED",
            "usip": "NO",
            "sp": "OFF",
            "rtspsessionidremap": "OFF",
            "clttimeout": 180,
            "svrtimeout": 360,
        },
    }

    servicegroup_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "servicegroup": {
            "servicegroupname": "sg_web",
            "state": "UP",
            "totalrequests": 50000,
            "totalresponses": 50000,
            "totalrequestbytes": 250000000,
            "totalresponsebytes": 500000000,
            "activemembers": 3,
            "avgserverttfb": 45,
            "primaryipaddress": "0.0.0.0",
            "primaryport": 0,
        },
    }

    write_fixture(config_dir / "servicegroup.json", servicegroup_config)
    write_fixture(stat_dir / "servicegroup.json", servicegroup_stat)

    # Interface fixtures
    print("  - interface (config + stat)")
    interface_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "interface": [
            {
                "id": "0/1",
                "devicename": "0/1",
                "description": "Management Interface",
                "flags": 224,
                "mtu": 1500,
                "vlan": 0,
                "mac": "00:0c:29:ab:cd:ef",
                "uptime": 864000,
                "downtime": 0,
                "reqmedia": "AUTO",
                "reqspeed": "AUTO",
                "reqduplex": "AUTO",
                "actmedia": "1000_T_FD",
                "actspeed": "1000",
                "actduplex": "FULL",
                "mode": "0",
                "state": "ENABLED",
                "autoneg": "ENABLED",
                "hamonitor": "ON",
                "haheartbeat": "OFF",
                "tagall": "OFF",
            },
            {
                "id": "1/1",
                "devicename": "1/1",
                "description": "Client Interface",
                "flags": 224,
                "mtu": 1500,
                "vlan": 0,
                "mac": "00:0c:29:ab:cd:f0",
                "uptime": 864000,
                "downtime": 0,
                "reqmedia": "AUTO",
                "reqspeed": "AUTO",
                "reqduplex": "AUTO",
                "actmedia": "1000_T_FD",
                "actspeed": "1000",
                "actduplex": "FULL",
                "mode": "0",
                "state": "ENABLED",
                "autoneg": "ENABLED",
                "hamonitor": "ON",
                "haheartbeat": "OFF",
                "tagall": "OFF",
            },
        ],
    }

    interface_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "interface": [
            {
                "id": "0/1",
                "rxpkts": 1000000,
                "rxbytes": 500000000,
                "rxerrors": 0,
                "rxdrops": 0,
                "txpkts": 950000,
                "txbytes": 450000000,
                "txerrors": 0,
                "txdrops": 0,
                "indisc": 0,
                "outdisc": 0,
                "fctls": 0,
                "hanums": 0,
                "stsstalls": 0,
                "txstalls": 0,
                "rxstalls": 0,
                "bdgmacmoved": 0,
                "bdgmuted": 0,
                "vmac": 0,
                "vmac6": 0,
                "totnetscalerpkts": 1950000,
            },
            {
                "id": "1/1",
                "rxpkts": 5000000,
                "rxbytes": 2500000000,
                "rxerrors": 0,
                "rxdrops": 0,
                "txpkts": 4800000,
                "txbytes": 2400000000,
                "txerrors": 0,
                "txdrops": 0,
                "indisc": 0,
                "outdisc": 0,
                "fctls": 0,
                "hanums": 0,
                "stsstalls": 0,
                "txstalls": 0,
                "rxstalls": 0,
                "bdgmacmoved": 0,
                "bdgmuted": 0,
                "vmac": 0,
                "vmac6": 0,
                "totnetscalerpkts": 9800000,
            },
        ],
    }

    write_fixture(config_dir / "interface.json", interface_config)
    write_fixture(stat_dir / "interface.json", interface_stat)

    # SSL Certificate fixtures
    print("  - sslcertkey (config)")
    expiry_ok = (datetime.now() + timedelta(days=60)).strftime("%b %d %H:%M:%S %Y GMT")
    expiry_warning = (datetime.now() + timedelta(days=20)).strftime("%b %d %H:%M:%S %Y GMT")
    expiry_critical = (datetime.now() + timedelta(days=5)).strftime("%b %d %H:%M:%S %Y GMT")

    sslcertkey_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "sslcertkey": [
            {
                "certkey": "cert_web",
                "cert": "/nsconfig/ssl/cert_web.pem",
                "key": "/nsconfig/ssl/cert_web.key",
                "inform": "PEM",
                "expirymonitor": "ENABLED",
                "notificationperiod": 30,
                "status": "Valid",
                "daystoexpiration": 60,
                "subject": "CN=web.example.com,O=Example Inc,C=US",
                "issuer": "CN=Example CA,O=Example Inc,C=US",
                "clientcertnotbefore": "Jan  1 00:00:00 2024 GMT",
                "clientcertnotafter": expiry_ok,
                "serialnumber": "1234567890ABCDEF",
            },
            {
                "certkey": "cert_warning",
                "cert": "/nsconfig/ssl/cert_warning.pem",
                "key": "/nsconfig/ssl/cert_warning.key",
                "inform": "PEM",
                "expirymonitor": "ENABLED",
                "notificationperiod": 30,
                "status": "Valid",
                "daystoexpiration": 20,
                "subject": "CN=warning.example.com,O=Example Inc,C=US",
                "issuer": "CN=Example CA,O=Example Inc,C=US",
                "clientcertnotbefore": "Jan  1 00:00:00 2024 GMT",
                "clientcertnotafter": expiry_warning,
                "serialnumber": "ABCDEF1234567890",
            },
            {
                "certkey": "cert_critical",
                "cert": "/nsconfig/ssl/cert_critical.pem",
                "key": "/nsconfig/ssl/cert_critical.key",
                "inform": "PEM",
                "expirymonitor": "ENABLED",
                "notificationperiod": 30,
                "status": "Valid",
                "daystoexpiration": 5,
                "subject": "CN=critical.example.com,O=Example Inc,C=US",
                "issuer": "CN=Example CA,O=Example Inc,C=US",
                "clientcertnotbefore": "Jan  1 00:00:00 2024 GMT",
                "clientcertnotafter": expiry_critical,
                "serialnumber": "FEDCBA0987654321",
            },
        ],
    }

    write_fixture(config_dir / "sslcertkey.json", sslcertkey_config)

    # nsconfig fixtures
    print("  - nsconfig (config)")
    nsconfig_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "nsconfig": {
            "ipaddress": "192.168.1.1",
            "netmask": "255.255.255.0",
            "nsvlan": 1,
            "ifnum": ["0/1", "1/1"],
            "tagged": "NO",
            "httpport": 80,
            "maxconn": 0,
            "maxreq": 0,
            "cip": "DISABLED",
            "cipheader": "",
            "cookieversion": "0",
            "securecookie": "ENABLED",
            "pmtumin": 576,
            "pmtutimeout": 10,
            "ftpportrange": "1024-65535",
            "crportrange": "1024-65535",
            "timezone": "GMT",
            "lastconfigchangedtime": "Wed Dec  4 10:30:15 2024",
        },
    }
    write_fixture(config_dir / "nsconfig.json", nsconfig_config)

    # nshardware fixtures
    print("  - nshardware (config)")
    nshardware_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "nshardware": {
            "hwdescription": "NetScaler Virtual Appliance",
            "sysid": "0x0",
            "manufactureday": 0,
            "manufacturemonth": 0,
            "manufactureyear": 0,
            "cpufrequncy": 2400,
            "numcpus": 4,
            "numcores": 4,
            "numpe": 1,
            "host": "ns01.example.com",
            "serialno": "VM-1234567890",
            "encodedserialno": "VM-1234567890",
            "disksize": 160000,
            "totalmemory": 8192,
            "additionalpe": 0,
        },
    }
    write_fixture(config_dir / "nshardware.json", nshardware_config)

    # nsversion fixtures
    print("  - nsversion (config)")
    nsversion_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "nsversion": {
            "installedversion": "NS14.1: Build 21.48.nc, Date: Jun 17 2024",
            "version": "NetScaler NS14.1",
            "mode": "1",
        },
    }
    write_fixture(config_dir / "nsversion.json", nsversion_config)

    # ntpsync fixtures
    print("  - ntpsync (config)")
    ntpsync_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "ntpsync": {"state": "ENABLED", "serverip": "", "servertype": "AUTO"},
    }
    write_fixture(config_dir / "ntpsync.json", ntpsync_config)

    # ntpstatus fixtures
    print("  - ntpstatus (config)")
    ntpstatus_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "ntpstatus": {
            "response": """     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*192.168.1.1     .GPS.            1 u   64  128  377    1.234   5.000   2.500
+192.168.1.2     .GPS.            1 u   64  128  377    1.234  10.000   1.000
+192.168.1.3     .GPS.            2 u   64  128  377    1.234  15.000   3.000
 192.168.1.4     .GPS.            3 u   64  128  377    1.234  20.000   4.000"""
        },
    }
    write_fixture(config_dir / "ntpstatus.json", ntpstatus_config)

    # systemfile fixtures (license files)
    print("  - systemfile (config)")

    # Create realistic license file content
    license_expiry = (datetime.now() + timedelta(days=365)).strftime("%d-%b-%Y")
    license_content = f"""SERVER this_host ANY
INCREMENT CNS_V3000_SERVER_PLT citrix 12.0 {license_expiry} 1 \\
    VENDOR_STRING=NetScaler:Platinum \\
    HOSTID=ANY SN=1234567890 START=01-jan-2024
INCREMENT CNS_WEBLOGGING citrix 12.0 {license_expiry} 1 \\
    VENDOR_STRING=NetScaler:WebLogging \\
    HOSTID=ANY SN=1234567890 START=01-jan-2024
INCREMENT CNS_SSL citrix 12.0 permanent 1 \\
    VENDOR_STRING=NetScaler:SSL \\
    HOSTID=ANY SN=1234567890 START=01-jan-2024
"""

    license_b64 = base64.b64encode(license_content.encode()).decode()

    systemfile_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "systemfile": [
            {
                "filename": "license.lic",
                "filelocation": "/nsconfig/license",
                "filesize": len(license_content),
                "filecontent": license_b64,
                "fileencoding": "BASE64",
            }
        ],
    }
    write_fixture(config_dir / "systemfile.json", systemfile_config)

    # hanode stat fixtures
    print("  - hanode (stat)")
    hanode_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "hanode": [
            {
                "name": "Node 0",
                "hacurstatus": "Primary",
                "hacurstate": "UP",
                "hamasterstate": "Primary",
                "haprop": "ENABLED",
                "hareceive": "ENABLED",
                "haheartbeats": "ENABLED",
                "deadinterval": 3,
                "hamonitor": "ENABLED",
                "hasync": "ENABLED",
                "routemonitor": "DISABLED",
                "hasyncfailurereason": "",
                "rsskeymismatch": "NO",
                "enaifaces": "1/1",
                "disifaces": "",
                "hamonifaces": "1/1",
                "pfifaces": "",
                "ifaces": "1/1",
            },
            {
                "name": "Node 1",
                "hacurstatus": "Secondary",
                "hacurstate": "UP",
                "hamasterstate": "Secondary",
                "haprop": "ENABLED",
                "hareceive": "ENABLED",
                "haheartbeats": "ENABLED",
                "deadinterval": 3,
                "hamonitor": "ENABLED",
                "hasync": "ENABLED",
                "routemonitor": "DISABLED",
                "hasyncfailurereason": "",
                "rsskeymismatch": "NO",
                "enaifaces": "1/1",
                "disifaces": "",
                "hamonifaces": "1/1",
                "pfifaces": "",
                "ifaces": "1/1",
            },
        ],
    }
    write_fixture(stat_dir / "hanode.json", hanode_stat)

    # Tier 2: vServer fixtures
    print("\n📦 Generating Tier 2 fixtures...")

    # VPN vServer
    print("  - vpnvserver (config + stat)")
    vpnvserver_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "vpnvserver": [
            {
                "name": "vpn_gateway",
                "servicetype": "SSL",
                "ipv46": "192.168.2.100",
                "port": 443,
                "range": 1,
                "state": "ENABLED",
                "authentication": "ON",
                "doublehop": "DISABLED",
                "icaonly": "OFF",
                "dtls": "ON",
                "maxaaausers": 0,
            }
        ],
    }

    vpnvserver_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "vpnvserver": [
            {
                "name": "vpn_gateway",
                "primaryipaddress": "192.168.2.100",
                "primaryport": 443,
                "type": "SSL",
                "state": "UP",
                "totalrequests": 5000,
                "totalresponses": 5000,
                "totalrequestbytes": 25000000,
                "totalresponsebytes": 50000000,
            }
        ],
    }

    write_fixture(config_dir / "vpnvserver.json", vpnvserver_config)
    write_fixture(stat_dir / "vpnvserver.json", vpnvserver_stat)

    # Authentication vServer
    print("  - authenticationvserver (config + stat)")
    authenticationvserver_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "authenticationvserver": [
            {
                "name": "auth_vs",
                "servicetype": "SSL",
                "ipv46": "192.168.2.101",
                "port": 443,
                "state": "ENABLED",
                "authentication": "ON",
                "authenticationdomain": "example.com",
            }
        ],
    }

    authenticationvserver_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "authenticationvserver": [
            {
                "name": "auth_vs",
                "primaryipaddress": "192.168.2.101",
                "primaryport": 443,
                "type": "SSL",
                "state": "UP",
                "totalrequests": 1000,
                "totalresponses": 1000,
            }
        ],
    }

    write_fixture(config_dir / "authenticationvserver.json", authenticationvserver_config)
    write_fixture(stat_dir / "authenticationvserver.json", authenticationvserver_stat)

    # CS vServer
    print("  - csvserver (config + stat)")
    csvserver_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "csvserver": [
            {
                "name": "cs_web",
                "servicetype": "HTTP",
                "ipv46": "192.168.2.102",
                "port": 80,
                "curstate": "UP",
                "sc": "OFF",
                "cacheable": "NO",
                "precedence": "RULE",
                "casesensitive": "ON",
                "somethod": "CONNECTION",
                "sopersistence": "DISABLED",
                "sopersistencetimeout": 2,
            }
        ],
    }

    csvserver_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "csvserver": [
            {
                "name": "cs_web",
                "primaryipaddress": "192.168.2.102",
                "primaryport": 80,
                "type": "CONTENT",
                "state": "UP",
                "totalrequests": 25000,
                "totalresponses": 25000,
                "totalrequestbytes": 125000000,
                "totalresponsebytes": 250000000,
            }
        ],
    }

    write_fixture(config_dir / "csvserver.json", csvserver_config)
    write_fixture(stat_dir / "csvserver.json", csvserver_stat)

    # GSLB vServer
    print("  - gslbvserver (config + stat)")
    gslbvserver_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "gslbvserver": [
            {
                "name": "gslb_site",
                "servicetype": "HTTP",
                "state": "ENABLED",
                "lbmethod": "ROUNDROBIN",
                "backuplbmethod": "ROUNDROBIN",
                "tolerance": 0,
                "persistencetype": "NONE",
                "timeout": 2,
                "mir": "DISABLED",
                "disableprimaryondown": "DISABLED",
                "dynamicweight": "DISABLED",
                "considereffectivestate": "NONE",
            }
        ],
    }

    gslbvserver_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "gslbvserver": [
            {
                "name": "gslb_site",
                "type": "HTTP",
                "state": "UP",
                "totalrequests": 10000,
                "totalresponses": 10000,
            }
        ],
    }

    write_fixture(config_dir / "gslbvserver.json", gslbvserver_config)
    write_fixture(stat_dir / "gslbvserver.json", gslbvserver_stat)

    # STA Server
    print("  - staserver (config + stat)")
    staserver_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "staserver": [
            {
                "name": "http://sta1.example.com",
                "staserver": "http://sta1.example.com",
                "staaddresstype": "IPV4",
            },
            {
                "name": "http://sta2.example.com",
                "staserver": "http://sta2.example.com",
                "staaddresstype": "IPV4",
            },
        ],
    }

    staserver_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "staserver": [
            {
                "name": "http://sta1.example.com",
                "staserver": "http://sta1.example.com",
                "stastate": "UP",
                "staauthfailures": 0,
                "totalrequests": 500,
                "totalresponses": 500,
            },
            {
                "name": "http://sta2.example.com",
                "staserver": "http://sta2.example.com",
                "stastate": "UP",
                "staauthfailures": 0,
                "totalrequests": 500,
                "totalresponses": 500,
            },
        ],
    }

    write_fixture(config_dir / "staserver.json", staserver_config)
    write_fixture(stat_dir / "staserver.json", staserver_stat)

    # SSL vServer (for bindings - optional)
    print("  - sslvserver (config + stat)")
    sslvserver_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "sslvserver": [
            {
                "vservername": "lb_ssl",
                "cleartextport": 0,
                "sslv3": "DISABLED",
                "tls1": "ENABLED",
                "tls11": "ENABLED",
                "tls12": "ENABLED",
                "tls13": "ENABLED",
                "dtls1": "DISABLED",
                "snienable": "DISABLED",
            }
        ],
    }

    sslvserver_stat = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "sslvserver": [
            {
                "vservername": "lb_ssl",
                "ssltotsessions": 1000,
                "ssltottransactions": 50000,
                "ssltotenc": 500000000,
                "ssltotdec": 500000000,
            }
        ],
    }

    write_fixture(config_dir / "sslvserver.json", sslvserver_config)
    write_fixture(stat_dir / "sslvserver.json", sslvserver_stat)

    # Backend Server
    print("  - server (config)")
    server_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "server": [
            {
                "name": "web1.example.com",
                "ipaddress": "10.1.1.10",
                "state": "ENABLED",
                "domainresolveretry": 5,
            },
            {
                "name": "web2.example.com",
                "ipaddress": "10.1.1.11",
                "state": "ENABLED",
                "domainresolveretry": 5,
            },
        ],
    }

    write_fixture(config_dir / "server.json", server_config)

    # NS Features
    print("  - nsfeature (config)")
    nsfeature_config = {
        "errorcode": 0,
        "message": "Done",
        "severity": "NONE",
        "nsfeature": {
            "feature": ["LB", "CS", "SSL", "GSLB", "SSLVPN", "AAA", "RESPONDER", "REWRITE"]
        },
    }

    write_fixture(config_dir / "nsfeature.json", nsfeature_config)

    print("\n✅ All fixtures generated!")
    print("📁 Total fixtures:")
    print(f"   - config: {len(list(config_dir.glob('*.json')))} files")
    print(f"   - stat: {len(list(stat_dir.glob('*.json')))} files")


def write_fixture(path: Path, data: dict):
    """Write fixture data to JSON file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    generate_fixtures()
