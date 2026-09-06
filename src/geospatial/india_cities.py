"""
India State → City dataset with WGS-84 coordinates.

Each city entry:  (display_name, api_query_name, latitude, longitude)

- display_name:   shown in the UI
- api_query_name: passed to get_live_weather() / get_forecast()
                  (uses the most recognisable English spelling for geocoding)
- latitude/longitude: WGS-84 coordinates from public geographic databases

Source: publicly available geographic data (Wikipedia, OpenStreetMap, IMD)
"""
from typing import Dict, List, Tuple

# (display_name, api_query_name, latitude, longitude)
CityEntry = Tuple[str, str, float, float]

INDIA_CITIES: Dict[str, List[CityEntry]] = {
    "Maharashtra": [
        ("Pune",                      "Pune",            18.5204,  73.8567),
        ("Mumbai",                    "Mumbai",           19.0760,  72.8777),
        ("Nagpur",                    "Nagpur",           21.1458,  79.0882),
        ("Nashik",                    "Nashik",           19.9975,  73.7898),
        ("Aurangabad",                "Aurangabad",       19.8762,  75.3433),
        ("Kolhapur",                  "Kolhapur",         16.7050,  74.2433),
        ("Solapur",                   "Solapur",          17.6854,  75.9044),
        ("Navi Mumbai",               "Navi Mumbai",      19.0330,  73.0297),
        ("Thane",                     "Thane",            19.2183,  72.9781),
        ("Amravati",                  "Amravati",         20.9374,  77.7796),
        ("Nanded",                    "Nanded",           19.1383,  77.3210),
        ("Sangli",                    "Sangli",           16.8524,  74.5815),
        ("Malegaon",                  "Malegaon",         20.5579,  74.5089),
        ("Jalgaon",                   "Jalgaon",          21.0077,  75.5626),
        ("Akola",                     "Akola",            20.7002,  77.0082),
        ("Latur",                     "Latur",            18.4088,  76.5604),
        ("Dhule",                     "Dhule",            20.9013,  74.7749),
        ("Ahmednagar",                "Ahmednagar",       19.0948,  74.7480),
        ("Chandrapur",                "Chandrapur",       19.9615,  79.2961),
        ("Parbhani",                  "Parbhani",         19.2704,  76.7748),
    ],
    "Karnataka": [
        ("Bengaluru",                 "Bengaluru",        12.9716,  77.5946),
        ("Mysuru",                    "Mysuru",           12.2958,  76.6394),
        ("Mangaluru",                 "Mangaluru",        12.9141,  74.8560),
        ("Hubballi",                  "Hubballi",         15.3647,  75.1240),
        ("Belagavi",                  "Belagavi",         15.8497,  74.4977),
        ("Kalaburagi",                "Kalaburagi",       17.3297,  76.8200),
        ("Ballari",                   "Ballari",          15.1394,  76.9214),
        ("Vijayapura",                "Vijayapura",       16.8302,  75.7100),
        ("Shivamogga",                "Shivamogga",       13.9299,  75.5681),
        ("Tumakuru",                  "Tumakuru",         13.3379,  77.1173),
        ("Davangere",                 "Davangere",        14.4644,  75.9218),
        ("Raichur",                   "Raichur",          16.2120,  77.3439),
        ("Hassan",                    "Hassan",           13.0068,  76.0996),
        ("Dharwad",                   "Dharwad",          15.4587,  75.0083),
        ("Udupi",                     "Udupi",            13.3409,  74.7421),
    ],
    "Delhi": [
        ("New Delhi",                 "New Delhi",        28.6139,  77.2090),
        ("Delhi",                     "Delhi",            28.7041,  77.1025),
        ("Dwarka",                    "Dwarka Delhi",     28.5823,  77.0594),
        ("Rohini",                    "Rohini Delhi",     28.7329,  77.1187),
        ("Noida",                     "Noida",            28.5355,  77.3910),
        ("Gurgaon",                   "Gurgaon",          28.4595,  77.0266),
        ("Faridabad",                 "Faridabad",        28.4089,  77.3178),
        ("Ghaziabad",                 "Ghaziabad",        28.6692,  77.4538),
    ],
    "Tamil Nadu": [
        ("Chennai",                   "Chennai",          13.0827,  80.2707),
        ("Coimbatore",                "Coimbatore",       11.0168,  76.9558),
        ("Madurai",                   "Madurai",           9.9252,  78.1198),
        ("Tiruchirappalli",           "Tiruchirappalli",  10.7905,  78.7047),
        ("Salem",                     "Salem",            11.6643,  78.1460),
        ("Tirunelveli",               "Tirunelveli",       8.7139,  77.7567),
        ("Tiruppur",                  "Tiruppur",         11.1085,  77.3411),
        ("Erode",                     "Erode",            11.3410,  77.7172),
        ("Vellore",                   "Vellore",          12.9165,  79.1325),
        ("Thoothukudi",               "Thoothukudi",       8.7642,  78.1348),
        ("Dindigul",                  "Dindigul",         10.3673,  77.9803),
        ("Thanjavur",                 "Thanjavur",        10.7870,  79.1378),
        ("Ooty",                      "Ooty",             11.4102,  76.6950),
        ("Kanyakumari",               "Kanyakumari",       8.0883,  77.5385),
    ],
    "Telangana": [
        ("Hyderabad",                 "Hyderabad",        17.3850,  78.4867),
        ("Warangal",                  "Warangal",         17.9689,  79.5941),
        ("Nizamabad",                 "Nizamabad",        18.6725,  78.0941),
        ("Karimnagar",                "Karimnagar",       18.4386,  79.1288),
        ("Ramagundam",                "Ramagundam",       18.7500,  79.4800),
        ("Khammam",                   "Khammam",          17.2473,  80.1514),
        ("Secunderabad",              "Secunderabad",     17.4399,  78.4983),
        ("Nalgonda",                  "Nalgonda",         17.0575,  79.2679),
        ("Adilabad",                  "Adilabad",         19.6640,  78.5320),
    ],
    "Gujarat": [
        ("Ahmedabad",                 "Ahmedabad",        23.0225,  72.5714),
        ("Surat",                     "Surat",            21.1702,  72.8311),
        ("Vadodara",                  "Vadodara",         22.3072,  73.1812),
        ("Rajkot",                    "Rajkot",           22.3039,  70.8022),
        ("Bhavnagar",                 "Bhavnagar",        21.7645,  72.1519),
        ("Jamnagar",                  "Jamnagar",         22.4707,  70.0577),
        ("Junagadh",                  "Junagadh",         21.5222,  70.4579),
        ("Gandhinagar",               "Gandhinagar",      23.2156,  72.6369),
        ("Anand",                     "Anand",            22.5645,  72.9289),
        ("Bharuch",                   "Bharuch",          21.7051,  72.9959),
        ("Navsari",                   "Navsari",          20.9467,  72.9520),
    ],
    "Rajasthan": [
        ("Jaipur",                    "Jaipur",           26.9124,  75.7873),
        ("Jodhpur",                   "Jodhpur",          26.2389,  73.0243),
        ("Kota",                      "Kota",             25.2138,  75.8648),
        ("Bikaner",                   "Bikaner",          28.0229,  73.3119),
        ("Ajmer",                     "Ajmer",            26.4499,  74.6399),
        ("Udaipur",                   "Udaipur",          24.5854,  73.7125),
        ("Bhilwara",                  "Bhilwara",         25.3407,  74.6313),
        ("Alwar",                     "Alwar",            27.5530,  76.6346),
        ("Sikar",                     "Sikar",            27.6094,  75.1399),
        ("Bharatpur",                 "Bharatpur",        27.2152,  77.4931),
        ("Jaisalmer",                 "Jaisalmer",        26.9157,  70.9083),
        ("Mount Abu",                 "Mount Abu",        24.5926,  72.7156),
    ],
    "Uttar Pradesh": [
        ("Lucknow",                   "Lucknow",          26.8467,  80.9462),
        ("Kanpur",                    "Kanpur",           26.4499,  80.3319),
        ("Agra",                      "Agra",             27.1767,  78.0081),
        ("Varanasi",                  "Varanasi",         25.3176,  82.9739),
        ("Allahabad",                 "Allahabad",        25.4358,  81.8463),
        ("Meerut",                    "Meerut",           28.9845,  77.7064),
        ("Bareilly",                  "Bareilly",         28.3670,  79.4304),
        ("Aligarh",                   "Aligarh",          27.8974,  78.0880),
        ("Moradabad",                 "Moradabad",        28.8386,  78.7733),
        ("Ghaziabad",                 "Ghaziabad",        28.6692,  77.4538),
        ("Gorakhpur",                 "Gorakhpur",        26.7606,  83.3732),
        ("Mathura",                   "Mathura",          27.4924,  77.6737),
    ],
    "West Bengal": [
        ("Kolkata",                   "Kolkata",          22.5726,  88.3639),
        ("Howrah",                    "Howrah",           22.5958,  88.2636),
        ("Durgapur",                  "Durgapur",         23.5204,  87.3119),
        ("Asansol",                   "Asansol",          23.6833,  86.9833),
        ("Siliguri",                  "Siliguri",         26.7271,  88.3953),
        ("Darjeeling",                "Darjeeling",       27.0360,  88.2627),
        ("Malda",                     "Malda",            25.0108,  88.1414),
        ("Bardhaman",                 "Bardhaman",        23.2324,  87.8615),
        ("Haldia",                    "Haldia",           22.0667,  88.0694),
        ("Krishnanagar",              "Krishnanagar",     23.4000,  88.5000),
    ],
    "Madhya Pradesh": [
        ("Bhopal",                    "Bhopal",           23.2599,  77.4126),
        ("Indore",                    "Indore",           22.7196,  75.8577),
        ("Gwalior",                   "Gwalior",          26.2183,  78.1828),
        ("Jabalpur",                  "Jabalpur",         23.1815,  79.9864),
        ("Ujjain",                    "Ujjain",           23.1765,  75.7885),
        ("Sagar",                     "Sagar",            23.8388,  78.7378),
        ("Rewa",                      "Rewa",             24.5362,  81.2982),
        ("Satna",                     "Satna",            24.5700,  80.8300),
        ("Dewas",                     "Dewas",            22.9623,  76.0508),
        ("Ratlam",                    "Ratlam",           23.3315,  75.0367),
        ("Khajuraho",                 "Khajuraho",        24.8318,  79.9199),
        ("Pachmarhi",                 "Pachmarhi",        22.4674,  78.4337),
    ],
    "Kerala": [
        ("Thiruvananthapuram",        "Thiruvananthapuram", 8.5241, 76.9366),
        ("Kochi",                     "Kochi",            9.9312,  76.2673),
        ("Kozhikode",                 "Kozhikode",        11.2588,  75.7804),
        ("Thrissur",                  "Thrissur",         10.5276,  76.2144),
        ("Kollam",                    "Kollam",           8.8932,  76.6141),
        ("Kannur",                    "Kannur",           11.8745,  75.3704),
        ("Alappuzha",                 "Alappuzha",         9.4981,  76.3388),
        ("Palakkad",                  "Palakkad",         10.7867,  76.6548),
        ("Malappuram",                "Malappuram",       11.0510,  76.0711),
        ("Kottayam",                  "Kottayam",          9.5916,  76.5222),
        ("Munnar",                    "Munnar",           10.0892,  77.0595),
    ],
    "Punjab": [
        ("Ludhiana",                  "Ludhiana",         30.9010,  75.8573),
        ("Amritsar",                  "Amritsar",         31.6340,  74.8723),
        ("Jalandhar",                 "Jalandhar",        31.3260,  75.5762),
        ("Patiala",                   "Patiala",          30.3398,  76.3869),
        ("Bathinda",                  "Bathinda",         30.2110,  74.9455),
        ("Mohali",                    "Mohali",           30.7046,  76.7179),
        ("Pathankot",                 "Pathankot",        32.2742,  75.6526),
        ("Hoshiarpur",                "Hoshiarpur",       31.5143,  75.9115),
        ("Firozpur",                  "Firozpur",         30.9254,  74.6060),
    ],
    "Haryana": [
        ("Faridabad",                 "Faridabad",        28.4089,  77.3178),
        ("Gurgaon",                   "Gurgaon",          28.4595,  77.0266),
        ("Panipat",                   "Panipat",          29.3909,  76.9635),
        ("Ambala",                    "Ambala",           30.3782,  76.7767),
        ("Hisar",                     "Hisar",            29.1492,  75.7217),
        ("Rohtak",                    "Rohtak",           28.8955,  76.6066),
        ("Karnal",                    "Karnal",           29.6857,  76.9905),
        ("Sonipat",                   "Sonipat",          28.9930,  77.0151),
        ("Yamunanagar",               "Yamunanagar",      30.1290,  77.2674),
        ("Kurukshetra",               "Kurukshetra",      29.9695,  76.8783),
    ],
    "Bihar": [
        ("Patna",                     "Patna",            25.5941,  85.1376),
        ("Gaya",                      "Gaya",             24.7955,  85.0002),
        ("Bhagalpur",                 "Bhagalpur",        25.2425,  86.9842),
        ("Muzaffarpur",               "Muzaffarpur",      26.1209,  85.3647),
        ("Purnia",                    "Purnia",           25.7771,  87.4753),
        ("Darbhanga",                 "Darbhanga",        26.1542,  85.8975),
        ("Begusarai",                 "Begusarai",        25.4182,  86.1272),
        ("Bihar Sharif",              "Bihar Sharif",     25.2014,  85.5239),
    ],
    "Odisha": [
        ("Bhubaneswar",               "Bhubaneswar",      20.2961,  85.8245),
        ("Cuttack",                   "Cuttack",          20.4625,  85.8828),
        ("Rourkela",                  "Rourkela",         22.2604,  84.8536),
        ("Brahmapur",                 "Brahmapur",        19.3150,  84.7941),
        ("Sambalpur",                 "Sambalpur",        21.4669,  83.9812),
        ("Puri",                      "Puri",             19.8134,  85.8315),
        ("Balasore",                  "Balasore",         21.4942,  86.9336),
    ],
    "Assam": [
        ("Guwahati",                  "Guwahati",         26.1445,  91.7362),
        ("Silchar",                   "Silchar",          24.8333,  92.7789),
        ("Dibrugarh",                 "Dibrugarh",        27.4728,  94.9120),
        ("Jorhat",                    "Jorhat",           26.7509,  94.2037),
        ("Nagaon",                    "Nagaon",           26.3481,  92.6840),
        ("Tinsukia",                  "Tinsukia",         27.4893,  95.3658),
        ("Tezpur",                    "Tezpur",           26.6338,  92.7926),
    ],
    "Jharkhand": [
        ("Ranchi",                    "Ranchi",           23.3441,  85.3096),
        ("Jamshedpur",                "Jamshedpur",       22.8046,  86.2029),
        ("Dhanbad",                   "Dhanbad",          23.7957,  86.4304),
        ("Bokaro",                    "Bokaro",           23.6693,  86.1511),
        ("Hazaribagh",                "Hazaribagh",       23.9987,  85.3611),
        ("Deoghar",                   "Deoghar",          24.4854,  86.6950),
    ],
    "Uttarakhand": [
        ("Dehradun",                  "Dehradun",         30.3165,  78.0322),
        ("Haridwar",                  "Haridwar",         29.9457,  78.1642),
        ("Rishikesh",                 "Rishikesh",        30.0869,  78.2676),
        ("Nainital",                  "Nainital",         29.3919,  79.4542),
        ("Mussoorie",                 "Mussoorie",        30.4598,  78.0664),
        ("Roorkee",                   "Roorkee",          29.8543,  77.8880),
    ],
    "Himachal Pradesh": [
        ("Shimla",                    "Shimla",           31.1048,  77.1734),
        ("Manali",                    "Manali",           32.2396,  77.1887),
        ("Dharamshala",               "Dharamshala",      32.2190,  76.3234),
        ("Kullu",                     "Kullu",            31.9579,  77.1095),
        ("Mandi",                     "Mandi",            31.7073,  76.9318),
        ("Solan",                     "Solan",            30.9093,  77.0963),
    ],
    "Goa": [
        ("Panaji",                    "Panaji",           15.4909,  73.8278),
        ("Margao",                    "Margao",           15.2832,  73.9862),
        ("Vasco da Gama",             "Vasco da Gama",    15.3982,  73.8113),
        ("Mapusa",                    "Mapusa",           15.5937,  73.8091),
        ("Calangute",                 "Calangute",        15.5440,  73.7528),
    ],
    "Andhra Pradesh": [
        ("Visakhapatnam",             "Visakhapatnam",    17.6868,  83.2185),
        ("Vijayawada",                "Vijayawada",       16.5062,  80.6480),
        ("Guntur",                    "Guntur",           16.3067,  80.4365),
        ("Nellore",                   "Nellore",          14.4426,  79.9865),
        ("Kurnool",                   "Kurnool",          15.8281,  78.0373),
        ("Rajahmundry",               "Rajahmundry",      17.0005,  81.8040),
        ("Tirupati",                  "Tirupati",         13.6288,  79.4192),
        ("Kakinada",                  "Kakinada",         16.9891,  82.2475),
        ("Kadapa",                    "Kadapa",           14.4673,  78.8242),
    ],
    "Chhattisgarh": [
        ("Raipur",                    "Raipur",           21.2514,  81.6296),
        ("Bhilai",                    "Bhilai",           21.1938,  81.3509),
        ("Bilaspur",                  "Bilaspur",         22.0796,  82.1391),
        ("Korba",                     "Korba",            22.3595,  82.7501),
        ("Durg",                      "Durg",             21.1904,  81.2849),
        ("Rajnandgaon",               "Rajnandgaon",      21.0974,  81.0376),
    ],
    "Jammu & Kashmir": [
        ("Srinagar",                  "Srinagar",         34.0837,  74.7973),
        ("Jammu",                     "Jammu",            32.7266,  74.8570),
        ("Leh",                       "Leh",              34.1526,  77.5771),
        ("Kargil",                    "Kargil",           34.5539,  76.1349),
        ("Anantnag",                  "Anantnag",         33.7311,  75.1487),
        ("Kupwara",                   "Kupwara",          34.5215,  74.2554),
    ],
    "Sikkim": [
        ("Gangtok",                   "Gangtok",          27.3389,  88.6065),
        ("Namchi",                    "Namchi",           27.1667,  88.3667),
        ("Gyalshing",                 "Gyalshing",        27.2833,  88.2500),
    ],
    "Meghalaya": [
        ("Shillong",                  "Shillong",         25.5788,  91.8933),
        ("Tura",                      "Tura",             25.5149,  90.2142),
        ("Jowai",                     "Jowai",            25.4513,  92.2009),
        ("Cherrapunji",               "Cherrapunji",      25.2800,  91.7200),
    ],
    "Manipur": [
        ("Imphal",                    "Imphal",           24.8170,  93.9368),
        ("Thoubal",                   "Thoubal",          24.6397,  94.0139),
        ("Bishnupur",                 "Bishnupur",        24.6240,  93.7748),
    ],
    "Tripura": [
        ("Agartala",                  "Agartala",         23.8315,  91.2868),
        ("Udaipur",                   "Udaipur Tripura",  23.5370,  91.4870),
        ("Dharmanagar",               "Dharmanagar",      24.3760,  92.1680),
    ],
    "Mizoram": [
        ("Aizawl",                    "Aizawl",           23.7271,  92.7176),
        ("Lunglei",                   "Lunglei",          22.8887,  92.7340),
    ],
    "Nagaland": [
        ("Kohima",                    "Kohima",           25.6601,  94.1100),
        ("Dimapur",                   "Dimapur",          25.9044,  93.7269),
    ],
    "Arunachal Pradesh": [
        ("Itanagar",                  "Itanagar",         27.0844,  93.6053),
        ("Naharlagun",                "Naharlagun",       27.1027,  93.6955),
        ("Tawang",                    "Tawang",           27.5861,  91.8594),
    ],
}


def get_states() -> List[str]:
    """Return sorted list of all Indian states."""
    return sorted(INDIA_CITIES.keys())


def get_cities_for_state(state: str) -> List[CityEntry]:
    """Return list of (display_name, api_name, lat, lon) for a state."""
    return INDIA_CITIES.get(state, [])


def get_city_display_names(state: str) -> List[str]:
    """Return list of city display names for a state."""
    return [entry[0] for entry in INDIA_CITIES.get(state, [])]


def get_city_entry(state: str, display_name: str):
    """
    Return (display_name, api_name, latitude, longitude) for a city.
    Returns None if not found.
    """
    for entry in INDIA_CITIES.get(state, []):
        if entry[0] == display_name:
            return entry
    return None


def get_coordinates(state: str, display_name: str):
    """
    Return (latitude, longitude, api_name) for a city.
    Returns (None, None, display_name) if not found.
    """
    entry = get_city_entry(state, display_name)
    if entry:
        return entry[2], entry[3], entry[1]
    return None, None, display_name
