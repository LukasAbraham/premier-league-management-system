SPONSOR_CHOICES = [
    ('EM', 'Emirates'),
    ('CZ', 'Cazoo'),
    ('DF', 'Dafabet'),
    ('HB', 'Hollywoodbets'),
    ('BD', 'Budweiser'),
    ('AX', 'American Express'),
    ('TH', '3'),
    ('CI', 'Cinch'),
    ('SK', 'Stake'),
    ('W8', 'W88'),
    ('SB', 'SBOTOP.net'),
    ('FB', 'FBS'),
    ('SC', 'Standard Chartered'),
    ('EA', 'Etihad Airways'),
    ('F8', 'Fun88'),
    ('SI', 'Sportsbet.io'),
    ('AI', 'AIA'),
    ('BW', 'Betway'),
    ('AP', 'AstroPay'),
    ('NK', 'Nike'),
    ('PM', 'Puma'),
    ('AD', 'Adidas'),
    ('PA', 'Paramount'),
    ('CS', 'Castore'),
    ('HM', 'Hummel'),
    ('MC', 'Macron'),
    ('UM', 'Umbro'),
    ('NA', 'N/A'),
]

STADIUM_CHOICES = [
    ('AN', 'Anfield'),
    ('BC', 'Brentford Community Stadium'),
    ('CG', 'City Ground'),
    ('CN', 'Carrow Road'),
    ('CF', 'Craven Cottage'),
    ('DC', 'Dean Court'),
    ('EL', 'Elland Road'),
    ('ES', 'Emirates Stadium'),
    ('ET', 'Etihad Stadium'),
    ('GP', 'Goodisan Park'),
    ('KP', 'King Power Stadium'),
    ('LS', 'London Stadium'),
    ('MS', 'Molineux Stadium'),
    ('OT', 'Old Trafford'),
    ('SP', 'Selhurst Park'),
    ('SJ', 'St James Park'),
    ('SM', "St Mary's Stadium"),
    ('SB', 'Stamford Bridge'),
    ('TA', 'The Amex'),
    ('TH', 'Tottenham Hotspur Stadium'),
    ('TM', 'Turf Moor'),
    ('VR', 'Vicarage Road'),
    ('VP', 'Villa Park'),
]

STATUS_CHOICES = [
    ('V', 'Valid'),
    ('I', 'Invalid'),
]

CITY_CHOICES = [
    ('BA', 'Bath'),
    ('BI', 'Birmingham'),
    ('BR', 'Bradford'),
    ('BH', 'Brighton and Hove'),
    ('BU', 'Bristol'),
    ('CA', 'Cambridge'),
    ('CN', 'Canterbury'),
    ('CR', 'Carlisle'),
    ('CM', 'Chelmsford'),
    ('CH', 'Chester'),
    ('CI', 'Chichester'),
    ('CO', 'Colchester'),
    ('CV', 'Coventry'),
    ('DE', 'Derby'),
    ('DO', 'Doncaster'),
    ('DU', 'Durham'),
    ('EL', 'Ely'),
    ('EX', 'Exeter'),
    ('GL', 'Gloucester'),
    ('HE', 'Hereford'),
    ('HU', 'Kingston upon Hull'),
    ('LA', 'Lancaster'),
    ('LE', 'Leeds'),
    ('LI', 'Leicester'),
    ('LC', 'Lichfield'),
    ('LN', 'Lincoln'),
    ('LV', 'Liverpool'),
    ('LO', 'London'),
    ('MA', 'Manchester'),
    ('MK', 'Milton Keynes'),
    ('NE', 'Newcastle upon Tyne'),
    ('NO', 'Norwich'),
    ('NG', 'Nottingham'),
    ('OX', 'Oxford'),
    ('PE', 'Peterborough'),
    ('PL', 'Plymouth'),
    ('PO', 'Portsmouth'),
    ('PR', 'Preston'),
    ('RI', 'Ripon'),
    ('SA', 'Salford'),
    ('SB', 'Salisbury'),
    ('SH', 'Sheffield'),
    ('SO', 'Southampton'),
    ('SE', 'Southend-on-Sea'),
    ('ST', 'St Albans'),
    ('SN', 'Stoke-on-Trent'),
    ('SU', 'Sunderland'),
    ('TR', 'Truro'),
    ('WA', 'Wakefield'),
    ('WE', 'Wells'),
    ('WS', 'Westminster'),
    ('WI', 'Winchester'),
    ('WO', 'Wolverhampton'),
    ('WR', 'Worcester'),
    ('YO', 'York'),
]

CUP_CHOICES_DICT = {
    'EPL': ('Premier League', 'epl.png'),
    'FA': ('FA Cup', 'fa_cup.png'),
    'EFL': ('EFL Cup', 'efl_cup.png'),
    'CS': ('Community Shield', 'community_shield.png'),
    'UEL': ('UEFA Europa League', 'uel.png'),
    'UCL': ('UEFA Champions League', 'ucl.png'),
}

CUP_CHOICES = [(k, v[0]) for k, v in CUP_CHOICES_DICT.items()]
