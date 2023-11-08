COUNTRY='Country'
EVENT_NAME='Event Name'
EVENT_ID='Event ID'
EVENT_VENUE='Event Venue'
COUNTRY_CODE='Country Code'
TIME_ZONE='Time Zone'
OPEN_DATE='Open Date'
MARKET_COUNT='Market Count'
KEY_NAME = {
  "jockey": "jockey_name",
  "trainer": "trainer_name",
  "horse": "horse_name",
  "condition": "track_condition",
  "track": "track_name",
  "distance": "distance",
}

START_FILTER_CNT = {
    "Last 10": 10,
    "Last 20": 20,
    "Last 50": 50,
    "Last 100": 100,
    "Last 200": 200,
    "Last 500": 500,
    "Last 1000": 1000,
    "Last 2000": 2000,
    "Last 5000": 5000,
}

TRACKS = {
    "Australia": {
        "METRO": [
            "RANDWICK",
            "RANDWICK-KENSINGTON",
            "ROSEHILL",
            "WARWICK FARM",
            "CANTERBURY",
            "FLEMINGTON",
            "CAULFIELD",
            "MOONEE VALLEY",
            "SANDOWN HILLSIDE",
            "SANDOWN LAKESIDE",
            "EAGLE FARM",
            "DOOMBEN",
            "MORPHETTVILLE",
            "ASCOT",
            "BELMONT",
            "DARWIN",
            "CANBERRA",
            "HOBART",
            "LAUNCESTON"
        ],
        "PROVINCIAL": [
            "HAWKESBURY",
            "GOSFORD",
            "WYONG",
            "NEWCASTLE",
            "KEMBLA GRANGE",
            "GEELONG",
            "MORNINGTON",
            "BALLARAT",
            "BENDIGO",
            "CRANBOURNE",
            "PAKENHAM",
            "SEYMOUR",
            "WERRIBEE",
            "GOLD COAST",
            "SUNSHINE COAST",
            "IPSWICH",
            "TOOWOOMBA",
            "MURRAY BRIDGE",
            "GAWLER",
            "OAKBANK",
            "BUNBURY",
            "PINJARRA",
            "ALBANY",
            "NORTHAM",
            "GERALDTON",
            "ALICE SPRINGS",
            "DEVONPORT"
        ],
        "COUNTRY": [
            "ALBURY",
            "ARMIDALE",
            "BALLINA",
            "BATHURST",
            "BEGA",
            "CESSNOCK",
            "COFFS HARBOUR",
            "DUBBO",
            "GOULBURN",
            "GRAFTON",
            "INVERELL",
            "LISMORE",
            "MUDGEE",
            "MURWILLUMBAH",
            "MUSWELLBROOK",
            "ORANGE",
            "PARKES",
            "QUEANBEYAN",
            "SCONE",
            "TAMWORTH",
            "TAREE",
            "WAGGA WAGGA",
            "WARRNAMBOOL",
            "WANGARATTA",
            "SALE",
            "ECHUCA",
            "SWAN HILL",
            "HAMILTON",
            "HORSHAM",
            "BAIRNSDALE",
            "COLAC",
            "WODONGA",
            "CAIRNS",
            "TOWNSVILLE",
            "MACKAY",
            "ROCKHAMPTON",
            "BUNDABERG",
            "ROMA",
            "WARWICK",
            "GATTON",
            "MOUNT GAMBIER",
            "PORT LINCOLN",
            "PORT AUGUSTA",
            "PENOLA",
            "STRATHALBYN",
            "MORPHETTVILLE",
            "BALAKLAVA",
            "NARACOORTE",
            "BROOME",
            "KALGOORLIE",
            "ESPERANCE BAY",
            "NARROGIN",
            "YORK",
            "KATHERINE",
            "TENNANT CREEK",
            "PIONEER PARK",
            "LONGFORD",
            "CARRICK"
        ]
    },
    "New South Wales": {
        "METRO": [
            "RANDWICK",
            "ROSEHILL",
            "WARWICK FARM",
            "CANTERBURY"
        ],
        "PROVINCIAL": [
            "HAWKESBURY",
            "GOSFORD",
            "WYONG",
            "NEWCASTLE",
            "KEMBLA GRANGE"
        ],
        "COUNTRY": [
            "ALBURY",
            "ARMIDALE",
            "BALLINA",
            "BATHURST",
            "BEGA",
            "CESSNOCK",
            "COFFS HARBOUR",
            "DUBBO",
            "GOULBURN",
            "GRAFTON",
            "INVERELL",
            "LISMORE",
            "MUDGEE",
            "MURWILLUMBAH",
            "MUSWELLBROOK",
            "ORANGE",
            "PARKES",
            "QUEANBEYAN",
            "SCONE",
            "TAMWORTH",
            "TAREE",
            "WAGGA WAGGA"
        ]
    },
    "Victoria": {
        "METRO": [
            "FLEMINGTON", "CAULFIELD", "MOONEE VALLEY", ""
        ],
        "PROVINCIAL": [
            "GEELONG", "MORNINGTON", "BALLARAT", "BENDIGO", "CRANBOURNE", "PAKENHAM", "SEYMOUR", "WERRIBEE"
        ],
        "COUNTRY": [
            "WARRNAMBOOL", "WANGARATTA", "SALE", "ECHUCA", "SWAN HILL", "HAMILTON", "HORSHAM", "BAIRNSDALE", "COLAC", "WODONGA"
        ]
    },
    "Queensland": {
        "METRO": ["EAGLE FARM", "DOOMBEN"],
        "PROVINCIAL": ["GOLD COAST", "SUNSHINE COAST", "IPSWICH", "TOOWOOMBA"],
        "COUNTRY": [
            "CAIRNS",
            "TOWNSVILLE",
            "MACKAY",
            "ROCKHAMPTON",
            "BUNDABERG",
            "ROMA",
            "WARWICK",
            "GATTON"
        ]
    },
    "Northern Territory": {
        "METRO": ["DARWIN"],
        "PROVINCIAL": ["ALICE SPRINGS"],
        "COUNTRY": ["KATHERINE", "TENNANT CREEK", "PIONEER PARK"]
    },
    "Western Australia": {
        "METRO": ["ASCOT", "BELMONT"],
        "PROVINCIAL": ["BUNBURY", "PINJARRA", "ALBANY", "NORTHAM", "GERALDTON"],
        "COUNTRY": ["BROOME", "KALGOORLIE", "ESPERANCE BAY", "Carnarvon", "NARROGIN", "YORK"]
    },
    "South Australia": {
        "METRO": ["MORPHETTVILLE"],
        "PROVINCIAL": ["MURRAY BRIDGE", "GAWLER", "OAKBANK"],
        "COUNTRY": [
            "MOUNT GAMBIER",
            "PORT LINCOLN",
            "PORT AUGUSTA",
            "PENOLA",
            "STRATHALBYN",
            "MORPHETTVILLE",
            "BALAKLAVA",
            "NARACOORTE"
        ]
    },
    "Tasmania": {
        "METRO": ["HOBART", "LAUNCESTON"],
        "PROVINCIAL": ["DEVONPORT"],
        "COUNTRY": ["LONGFORD", "CARRICK"]
    }
}