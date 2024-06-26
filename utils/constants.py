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

CLASSES = {
    "Group 1 Races": 10,
    "Group 2 Races": 9.5,
    "Group 3 Races": 9,
    "Listed Races": 8,
    "Weight-for-Age Races": 8,
    "Set Weight plus Penalties": 6.5,
    "Special Handicap": 6,
    "Set Weights Races": 6,
    "Open Handicap": 7,
    "Benchmark 100": 7.5,
    "Benchmark 95": 7,
    "Benchmark 94": 7.25,
    "Benchmark 90": 6.5,
    "Benchmark 89": 6.75,
    "Benchmark 85": 6,
    "Benchmark 84": 5.75,
    "Benchmark 80": 5.5,
    "Benchmark 78": 5.25,
    "Benchmark 75": 5,
    "Benchmark 74": 4.75,
    "Benchmark 70": 4.5,
    "Benchmark 68": 4.25,
    "Benchmark 66": 4,
    "Benchmark 65": 4,
    "Benchmark 64": 3.75,
    "Benchmark 62": 3.75,
    "Benchmark 60": 3.5,
    "Benchmark 58": 3.25,
    "Benchmark 55": 3,
    "Benchmark 54": 3,
    "Benchmark 52": 2.75,
    "Benchmark 50": 2.75,
    "Benchmark 46": 2,
    "Benchmark 45": 2,
    "Benchmark 40": 1.5,
    "Class 1": 3,
    "Class 2": 3.5,
    "Class 3": 4,
    "Class 4": 4.5,
    "Class 5": 5,
    "Class 6": 5.5,
    "Maiden": 1,
    "Rst 0 Met Win-LY": 2.75,
    "RS0LY": 2.75,
    "RST52": 3,
    "RST53": 3,
    "RST54": 3.25,
    "RST55": 3.25,
    "RST56": 3.5,
    "RST57": 3.5,
    "RST58": 3.75,
    "RST59": 3.75,
    "RST60": 3.5,
    "RST61": 3.75,
    "RST62": 3.75,
    "RST64": 3.75,
    "RST65": 4,
    "RST66": 4.25,
    "RST68": 4.25,
    "RST70": 4.5,
    "RST72": 4.75,
    "RST74": 4.75,
    "RST75": 5,
    "RST76": 5.25,
    "RST78": 5.25,
    "RST80": 5.5,
    "RST82": 5.75,
    "RST84": 5.75,
    "RST85": 6,
    "RST86": 6.25,
    "RST88": 6.25,
    "RST90": 6.5,
    "Restricted 55": 3.25,
    "Restricted 58": 3.5,
    "Rs0MW": 2.5,
    "Rs1MW": 3,
    "Griff G-Open": 7,
    "Cls A": 2.5,
    "Class A": 2.5,
    "Cls B": 2.5,
    "Class B": 2.5,
    "Cls C": 2.5,
    "Class C": 2.5,
    "HiWgt": 5,
    "High Weight": 5,
    "JMPFL": 4,
    "Jumper Flat": 4,
    "Nov": 2,
    "Novice": 2,
    "Stpl": 6,
    "Hurdle": 5,
    "Hrdle": 5,
}

COLOR_RESP = {
    'b': 'b',
    'b/br': 'b',
    'bl': 'bl',
    'br': 'br',
    'br/bl': 'br',
    'gr': 'gr',
    'gr/b': 'b',
    'gr/br': 'br',
    'gr/bl': 'bl',
    'gr/ch': 'ch',
    'gr/ro': 'gr',
    'ch': 'ch',
    'du/ch': 'ch',
    'wh': 'gr',
    'wh/b': 'b',
    'ro': 'gr',
    'du': 'ch',
    'pa': 'bl',
    'ta': 'br',
    'pi': 'gr',
    'pl': 'b',
    'ap': 'gr'
}

CONDITION = {
    'F': 'FIRM',
    'G': 'GOOD',
    'H': 'HEAVY',
    'D': 'DEAD',
    'S': 'SOFT',
    'Y': 'SYNTHETIC',
    'O': 'SOFT'
}