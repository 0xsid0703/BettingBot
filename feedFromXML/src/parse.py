import os

import xml.etree.ElementTree as ET
from datetime import datetime

DATA_DIR = "feedFromXML/data"
FORM_DIR = "mr_form"
FIELD_DIR = "mr_fields"
START_DATE="13/9/2023"

def getHorseObj(horse_obj):
    db_obj = horse_obj.attrib
    for child in horse_obj:
        if child.tag == "trainer":
            trainer = child.attrib
            trainer['statistics'] = []
            statistics = child.find ("statistics")
            for statistic in statistics:
                trainer['statistics'].append (statistic.attrib)
            db_obj['trainer'] = trainer
            continue
        if child.tag == "statistics":
            db_obj["statistics"] = []
            for statistic in child:
                db_obj['statistics'].append (statistic.attrib)
            continue
        if child.tag == "gear_changes":
            db_obj["gear_changes"] = []
            for gear_change in child:
                db_obj['gear_changes'].append (gear_change.attrib)
            continue
        if child.tag == "jockey":
            db_obj["jockey"] = child.attrib
            db_obj['jockey']['statistics'] = []
            statistics = child.find ("statistics")
            if statistics is None: continue
            for statistic in statistics:
                db_obj['jockey']['statistics'].append (statistic.attrib)
            continue
        if child.tag == "forms":
            forms = []
            for form in child:
                form_obj = {}
                for form_child in form:
                    if form_child.tag == "classes":
                        classes = []
                        for class_obj in form_child:
                            classes.append ({class_obj.tag: class_obj.text})
                        form_obj['classes'] = classes
                        continue
                    if form_child.tag == "other_runners":
                        runners = []
                        for runner_obj in form_child:
                            runners.append (runner_obj.attrib)
                        form_obj['other_runners'] = runners
                        continue
                    if form_child.text is not None: form_obj[form_child.tag] = form_child.text
                    if form_child.attrib != {}: form_obj[form_child.tag] = form_child.attrib
                forms.append (form_obj)
            db_obj['forms'] = forms
            continue
        if child.attrib != {}: db_obj[child.tag] = child.attrib
        if child.text is not None: db_obj[child.tag] = child.text
    return db_obj
        
def getRaceObj(race_obj):
    db_obj = race_obj.attrib

    for child in race_obj:
        if child.tag == "classes":
            db_obj['classes'] = {}
            for class_child in child:
                db_obj['classes'][class_child.tag] = class_child.text
            continue
        if child.tag == "prizes":
            db_obj['prizes'] = []
            for prize_child in child:
                db_obj['prizes'].append (prize_child.attrib)
            continue
        if child.tag == "records":
            db_obj['records'] = []
            for tracking_record in child:
                tracking_obj = {}
                for t_child in tracking_record:
                    if t_child.tag == "horse":
                        tracking_obj['horse'] = t_child.attrib
                        for horse_child in t_child:
                            if horse_child.attrib != {}: tracking_obj['horse'][horse_child.tag] = horse_child.attrib
                            if horse_child.text is not None: tracking_obj['horse'][horse_child.tag] = horse_child.text
                        continue

                    if t_child.text is not None: tracking_obj[t_child.tag] = t_child.text
                    if t_child.attrib != {}: tracking_obj[t_child.tag] = t_child.attrib
                db_obj['records'].append (tracking_obj)
            continue

        if child.tag == 'horses':
            db_obj['horses'] = []
            for horse in child:
                db_obj['horses'].append (getHorseObj(horse))
            continue

        if child.text is not None:
            db_obj[child.tag] = child.text
        if child.attrib != {}:
            db_obj[child.tag] = child.attrib
    return db_obj

# def main():
def parse():
    cur_dir = os.getcwd()

    form_file_list = os.listdir(os.path.join(cur_dir, DATA_DIR, FORM_DIR))
    form_file_dir = os.path.join(DATA_DIR, FORM_DIR)

    rlt = []
    for form_file in form_file_list:
        db_obj = {}
        tree = ET.parse(os.path.join(form_file_dir, form_file))
        root = tree.getroot()
        for child in root:
            if child.tag == "races":
                db_obj['races'] = []
                for race in child:
                    db_obj['races'].append (getRaceObj(race))
                continue
            if child.tag == "track":
                if 'name' in child.attrib: db_obj['name'] = child.attrib['name']
                if 'id' in child.attrib: db_obj['id'] = child.attrib['id']
                if 'expected_condition' in child.attrib: db_obj['expected_condition'] = child.attrib['expected_condition']
                if 'club' in child.attrib: db_obj['club'] = child.attrib['club']
                if 'track_surface' in child.attrib: db_obj['track_surface'] = child.attrib['track_surface']
                if 'location' in child.attrib: db_obj['location'] = child.attrib['location']
                if 'country' in child.attrib: db_obj['country'] = child.attrib['country']
                if 'state' in child.attrib: db_obj['state'] = child.attrib['state']
                if 'track_3char_abbrev' in child.attrib: db_obj['track_3char_abbrev'] = child.attrib['track_3char_abbrev']
                if 'track_4char_abbrev' in child.attrib: db_obj['track_4char_abbrev'] = child.attrib['track_4char_abbrev']
                if 'track_6char_abbrev' in child.attrib: db_obj['track_6char_abbrev'] = child.attrib['track_6char_abbrev']
                if 'night_meeting' in child.attrib: db_obj['night_meeting'] = child.attrib['night_meeting']
                continue
            if child.text is not None:
                db_obj[child.tag] = child.text
            if child.attrib != {}:
                db_obj[child.tag] = child.attrib
        rlt.append (db_obj)
    
    return rlt

def buildProfile():
    cur_dir = os.getcwd()

    form_file_list = os.listdir(os.path.join(cur_dir, DATA_DIR, FORM_DIR))
    form_file_dir = os.path.join(DATA_DIR, FORM_DIR)

    rlt = []
    for form_file in form_file_list:
        db_obj = {}
        tree = ET.parse(os.path.join(form_file_dir, form_file))
        root = tree.getroot()
        for child in root:
            if child.tag == "races":
                db_obj['races'] = []
                for race in child:
                    db_obj['races'].append (getRaceObj(race))
                continue
            if child.tag == "track":
                if 'name' in child.attrib: db_obj['name'] = child.attrib['name']
                if 'id' in child.attrib: db_obj['id'] = child.attrib['id']
                if 'expected_condition' in child.attrib: db_obj['expected_condition'] = child.attrib['expected_condition']
                if 'club' in child.attrib: db_obj['club'] = child.attrib['club']
                if 'track_surface' in child.attrib: db_obj['track_surface'] = child.attrib['track_surface']
                if 'location' in child.attrib: db_obj['location'] = child.attrib['location']
                if 'country' in child.attrib: db_obj['country'] = child.attrib['country']
                if 'state' in child.attrib: db_obj['state'] = child.attrib['state']
                if 'track_3char_abbrev' in child.attrib: db_obj['track_3char_abbrev'] = child.attrib['track_3char_abbrev']
                if 'track_4char_abbrev' in child.attrib: db_obj['track_4char_abbrev'] = child.attrib['track_4char_abbrev']
                if 'track_6char_abbrev' in child.attrib: db_obj['track_6char_abbrev'] = child.attrib['track_6char_abbrev']
                if 'night_meeting' in child.attrib: db_obj['night_meeting'] = child.attrib['night_meeting']
                continue
            if child.text is not None:
                db_obj[child.tag] = child.text
            if child.attrib != {}:
                db_obj[child.tag] = child.attrib
        rlt.append (db_obj)
    
    return rlt

def buildRaceProfile():
    cur_dir = os.getcwd()

    form_file_list = os.listdir(os.path.join(cur_dir, DATA_DIR, FORM_DIR))
    form_file_dir = os.path.join(DATA_DIR, FORM_DIR)

    rlt = []
    btracks = []
    for form_file in form_file_list:
        tree = ET.parse(os.path.join(form_file_dir, form_file))
        root = tree.getroot()
        if root is None: continue
        
        homeTrack = root.find("track")
        homeTrackAttrib = homeTrack.attrib

        dateObj = root.find("date")
        trackDate = datetime.strptime(dateObj.text, "%d/%m/%Y")
        if START_DATE is not None and trackDate < datetime.strptime(START_DATE, "%d/%m/%Y"): continue
        print (trackDate)

        races = root.find("races")
        if races is None: continue
        
        races = races.findall("race")
        if races  is None: continue
        if len(races) == 0: continue
        for race in races:
            
            # raceRestriction = race.find ("restrictions")
            # if raceRestriction is not None:
            #     tmpRace['race_restriction_age'] = raceRestriction.attrib['age'] if 'age' in raceRestriction.attrib else '0'
            #     tmpRace['race_restriction_jockey'] = raceRestriction.attrib['jockey'] if 'jockey' in raceRestriction.attrib else '0'
            # raceWeightType = race.find ("weight_type")
            # if raceWeightType is not None: tmpRace['race_weight_type'] = raceWeightType.text
            # minHcpWeight = race.find ("min_hcp_weight")
            # if minHcpWeight is not None: tmpRace['race_min_hcp_weight'] = minHcpWeight.text
            raceClasses = race.find ('classes')
            
            raceType = race.find ("race_type")
            raceDistance = race.find ("distance")
            
            racePrizes = race.find ("prizes")
            # if racePrizes is not None:
            #     tmpRace['prizes'] = []
            #     for prize in racePrizes:
            #         tmpRace['prizes'].append ({prize.attrib['type']: int(prize.attrib['value'])})
            raceStartTime = race.find ("start_time")

            horses = race.find("horses")
            if horses is None: continue
            horses = horses.findall("horse")
            if len(horses) == 0: continue

            # tmpHorses = []

            for horse in horses:
                tmpRace = {}
                tmpRace['main_track_name'] = homeTrackAttrib['name'] if 'name' in homeTrackAttrib else ''
                tmpRace['main_track_id'] = homeTrackAttrib['id'] if 'id' in homeTrackAttrib else ''
                tmpRace['main_track_surface'] = homeTrackAttrib['track_surface'] if 'track_surface' in homeTrackAttrib else ''
                tmpRace['main_track_3char_abbrev'] = homeTrackAttrib['track_3char_abbrev'] if 'track_3char_abbrev' in homeTrackAttrib else ''
                tmpRace['main_track_condition'] = homeTrackAttrib['expected_condition'] if 'expected_condition' in homeTrackAttrib else ''
                tmpRace['main_track_club'] = homeTrackAttrib['club'] if 'club' in homeTrackAttrib else ''
                tmpRace['main_track_country'] = homeTrackAttrib['country'] if 'country' in homeTrackAttrib else ''
                tmpRace['main_race_num'] = race.attrib['number'] if 'number' in race.attrib else ''
                tmpRace['main_race_name'] = race.attrib['name'] if 'name' in race.attrib else ''
                tmpRace['main_race_id'] = race.attrib['id'] if 'id' in race.attrib else ''
                tmpRace['main_race_nominations_number'] = race.attrib['nominations_number'] if 'nominations_number' in race.attrib else ''
                tmpRace['date'] = datetime.strptime(dateObj.text, "%d/%m/%Y")
                if raceType is not None: tmpRace ['race_type'] = raceType.text
                if raceStartTime is not None:
                    tmpRace['start_time'] = datetime.strptime ("%s %s" % (dateObj.text, raceStartTime.text), "%d/%m/%Y %I:%M%p")
                
                if raceDistance is not None:
                    tmpRace['distance'] = raceDistance.attrib['metres'] if 'metres' in raceDistance.attrib else 0
                for classObj in raceClasses:
                    if classObj.tag == 'class':
                        tmpRace['class'] = classObj.text
                    if classObj.tag == 'class_id':
                        tmpRace['class_id'] = classObj.text
                if racePrizes is not None:
                    tmpRace['prizes'] = []
                    for prize in racePrizes:
                        tmpRace['prizes'].append ({prize.attrib['type']: int(prize.attrib['value'])})

                horseAttrib = horse.attrib

                tmpRace['horse_name'] = horseAttrib['name'] if 'name' in horseAttrib else ''
                tmpRace['horse_country'] = horseAttrib['country'] if 'country' in horseAttrib else ''
                tmpRace['horse_age'] = horseAttrib['age'] if 'age' in horseAttrib else ''
                tmpRace['horse_colour'] = horseAttrib['colour'] if 'colour' in horseAttrib else ''
                tmpRace['horse_sex'] = horseAttrib['sex'] if 'sex' in horseAttrib else ''
                tmpRace['horse_id'] = horseAttrib['id'] if 'id' in horseAttrib else ''

                trainer = horse.find('trainer')
                trainerAttrib = trainer.attrib

                sire = horse.find('sire')
                sireAttrib = sire.attrib

                dam = horse.find('dam')
                damAttrib = dam.attrib

                sire_dam = horse.find('sire_of_dam')
                sireDamAttrib = sire_dam.attrib

                # horsePrizeMoney = horse.find ("prizemoney_won")
                # horseLastFourStarts = horse.find ("last_four_starts")
                # horseLastTenStarts = horse.find ("last_ten_starts")
                # horseLastFifteenStarts = horse.find ("last_fifteen_starts")
                # horseLastTwentyStarts = horse.find ("last_twenty_starts")
                # horseFf5Dry = horse.find ("FF5_dry")
                # horseFf5Wet = horse.find ("FF5_wet")
                # horseFfDryRating100 = horse.find ("FF_Dry_Rating_100")
                # horseFfWetRating100 = horse.find ("FF_Wet_Rating_100")
                horseCurrentBlinkerInd = horse.find ("current_blinker_ind")
                # horseWinDistances = horse.find ("win_distances")
                horseRunningGear = horse.find ("running_gear")
                horseGearChanges = horse.find ("gear_changes")
                # horseFormComments = horse.find ("form_comments")
                horseWeight = horse.find ("weight")
                horseWeightAttrib = horseWeight.attrib if horseWeight is not None else None
                horseTabNo = horse.find ("tab_no")
                horseBarrier = horse.find ("barrier")
                horseSilk = horse.find ("horse_colours_image")
                # horseMarket = horse.find ("market")
                # horseMarketAttrib = horseMarket.attrib
                # horseComments = horse.find ("comments")

                jockey = horse.find('jockey')
                jockeyAttrib = jockey.attrib

                win_p = horse.find('win_percentage')
                place_p = horse.find('place_percentage')

                # tmpHorse['sire_name'] = sireAttrib['name'] if 'name' in sireAttrib else ''
                # tmpHorse['sire_country'] = sireAttrib['country'] if 'country' in sireAttrib else ''
                # tmpHorse['sire_id'] = int(sireAttrib['id']) if 'id' in sireAttrib else ''

                # tmpHorse['dam_name'] = damAttrib['name'] if 'name' in damAttrib else ''
                # tmpHorse['dam_country'] = damAttrib['country'] if 'country' in damAttrib else ''
                # tmpHorse['dam_id'] = int(damAttrib['id']) if 'id' in damAttrib else ''

                # tmpHorse['sire_dam_name'] = sireDamAttrib['name'] if 'name' in sireDamAttrib else ''
                # tmpHorse['sire_dam_country'] = sireDamAttrib['country'] if 'country' in sireDamAttrib else ''
                # tmpHorse['sire_dam_id'] = sireDamAttrib['id'] if 'id' in sireDamAttrib else ''

                tmpRace['main_trainer_name'] = trainerAttrib['name'] if 'name' in trainerAttrib else ''
                tmpRace['main_trainer_firstname'] = trainerAttrib['firstname'] if 'firstname' in trainerAttrib else ''
                tmpRace['main_trainer_surname'] = trainerAttrib['surname'] if 'surname' in trainerAttrib else ''
                tmpRace['main_trainer_id'] = int(trainerAttrib['id']) if 'id' in trainerAttrib else -1

                tmpRace['main_jockey_name'] = jockeyAttrib['name'] if 'name' in jockeyAttrib else ''
                tmpRace['main_jockey_firstname'] = jockeyAttrib['firstname'] if 'firstname' in jockeyAttrib else ''
                tmpRace['main_jockey_surname'] = jockeyAttrib['surname'] if 'surname' in jockeyAttrib else ''
                tmpRace['main_jockey_id'] = int(jockeyAttrib['id']) if 'id' in jockeyAttrib else -1
                tmpRace['main_jockey_riding_weight'] = float(jockeyAttrib['riding_weight']) if 'riding_weight' in jockeyAttrib and  len(jockeyAttrib['riding_weight'].strip()) > 0 else -1
                tmpRace['main_jockey_apprentice_indicator'] = jockeyAttrib['apprentice_indicator'] if 'apprentice_indicator' in jockeyAttrib else ''
                tmpRace['main_jockey_allowance_weight'] = float(jockeyAttrib['allowance_weight']) if 'allowance_weight' in jockeyAttrib else 0


                tmpRace['win_percentage'] = float(win_p.text) if win_p is not None else 0
                tmpRace['place_percentage'] = float(place_p.text) if place_p is not None else 0
                tmpRace['tab_no'] = int(horseTabNo.text) if horseTabNo is not None else 0
                tmpRace['current_blinker_ind'] = horseCurrentBlinkerInd.text if horseCurrentBlinkerInd is not None else 'N'

                tmpRace['gear_change'] = []
                for gearChange in horseGearChanges:
                    tmpRace['gear_change'].append (gearChange.attrib)
                
                tmpRace['running_gear'] = []
                for gearItem in horseRunningGear:
                    tmpRace['running_gear'].append (gearItem.text)

                # tmpHorse['prize_money'] = horsePrizeMoney.text if horsePrizeMoney is not None else 0
                # tmpHorse['last_four_starts'] = horseLastFourStarts.text if horseLastFourStarts is not None else ''
                # tmpHorse['last_ten_starts'] = horseLastTenStarts.text if horseLastTenStarts is not None else ''
                # tmpHorse['last_fifteen_starts'] = horseLastFifteenStarts.text if horseLastFifteenStarts is not None else ''
                # tmpHorse['last_twenty_starts'] = horseLastTwentyStarts.text if horseLastTwentyStarts is not None else ''
                # tmpHorse['FF5_dry'] = horseFf5Dry.text if horseFf5Dry is not None else 0
                # tmpHorse['FF5_wet'] = horseFf5Wet.text if horseFf5Wet is not None else 0
                # tmpHorse['FF_Dry_Rating_100'] = horseFfDryRating100.text if horseFfDryRating100 is not None else 0
                # tmpHorse['FF_Wet_Rating_100'] = horseFfWetRating100.text if horseFfWetRating100 is not None else 0
                # tmpHorse['current_blinker_ind'] = horseCurrentBlinkerInd.text if horseCurrentBlinkerInd is not None else ''
                # tmpHorse['form_comments'] = horseFormComments.text if horseFormComments is not None else ''
                # tmpHorse['horse_comments'] = horseComments.text if horseComments is not None else ''
                tmpRace['weight_allocated'] = horseWeightAttrib['allocated'] if horseWeightAttrib is not None else 0
                tmpRace['weight_total'] = horseWeightAttrib['total'] if horseWeightAttrib is not None else 0
                # tmpHorse['horse_price'] = horseMarketAttrib['price'] if horseMarketAttrib is not None else 0
                # tmpHorse['horse_price_decimal'] = horseMarketAttrib['price_decimal'] if horseMarketAttrib is not None else 0
                # tmpHorse['horse_tab_no'] = horseTabNo.text if horseTabNo is not None else 0
                tmpRace['horse_barrier'] = horseBarrier.text if horseBarrier is not None else 0
                tmpRace['horse_silk'] = horseSilk.text if horseSilk is not None else ''
                # tmpHorse['win_distances'] = []
                # for win_distance in horseWinDistances:
                #     tmpHorse['win_distances'].append ({"distance": win_distance.attrib['distance'], "wins": win_distance.attrib['wins']})
                # tmpHorses.append (tmpHorse)
                btracks.append (tmpRace)

                forms = horse.find("forms")
                if forms is None: continue
                forms = forms.findall("form")
                if len(forms) == 0: continue
                for form in forms:
                    tmp = {}
                    tmp['horse_name'] = horseAttrib['name'] if 'name' in horseAttrib else ''
                    tmp['horse_country'] = horseAttrib['country'] if 'country' in horseAttrib else ''
                    tmp['horse_age'] = int(horseAttrib['age']) if 'age' in horseAttrib else -1
                    tmp['horse_colour'] = horseAttrib['colour'] if 'colour' in horseAttrib else ''
                    tmp['horse_sex'] = horseAttrib['sex'] if 'sex' in horseAttrib else ''
                    tmp['horse_id'] = int(horseAttrib['id']) if 'id' in horseAttrib else -1
                    tmp['horse_foaling_date'] = datetime.strptime(horseAttrib['foaling_date'], "%d/%m/%Y") if 'foaling_date' in horseAttrib else None

                    tmp['home_track_name'] = homeTrackAttrib['name'] if 'name' in homeTrackAttrib else ''
                    tmp['home_track_id'] = homeTrackAttrib['id'] if 'id' in homeTrackAttrib else ''
                    tmp['home_track_surface'] = homeTrackAttrib['track_surface'] if 'track_surface' in homeTrackAttrib else ''
                    tmp['home_track_3char_abbrev'] = homeTrackAttrib['track_3char_abbrev'] if 'track_3char_abbrev' in homeTrackAttrib else ''
                    tmp['home_track_condition'] = homeTrackAttrib['expected_condition'] if 'expected_condition' in homeTrackAttrib else ''
                    tmp['home_track_country'] = homeTrackAttrib['country'] if 'country' in homeTrackAttrib else ''

                    tmp['home_race_num'] = race.attrib['number'] if 'number' in race.attrib else ''
                    tmp['home_race_name'] = race.attrib['name'] if 'name' in race.attrib else ''
                    tmp['home_race_id'] = race.attrib['id'] if 'id' in race.attrib else ''

                    tmp['home_date'] = datetime.strptime(dateObj.text, "%d/%m/%Y")
                    
                    tmp['sire_name'] = sireAttrib['name'] if 'name' in sireAttrib else ''
                    tmp['sire_country'] = sireAttrib['country'] if 'country' in sireAttrib else ''
                    tmp['sire_id'] = int(sireAttrib['id']) if 'id' in sireAttrib else ''

                    tmp['dam_name'] = damAttrib['name'] if 'name' in damAttrib else ''
                    tmp['dam_country'] = damAttrib['country'] if 'country' in damAttrib else ''
                    tmp['dam_id'] = int(damAttrib['id']) if 'id' in damAttrib else ''

                    tmp['sire_dam_name'] = sireDamAttrib['name'] if 'name' in sireDamAttrib else ''
                    tmp['sire_dam_country'] = sireDamAttrib['country'] if 'country' in sireDamAttrib else ''
                    tmp['sire_dam_id'] = sireDamAttrib['id'] if 'id' in sireDamAttrib else ''
                    
                    tmp['trainer_name'] = trainerAttrib['name'] if 'name' in horseAttrib else ''
                    tmp['trainer_firstname'] = trainerAttrib['firstname'] if 'firstname' in horseAttrib else ''
                    tmp['trainer_surname'] = trainerAttrib['surname'] if 'surname' in horseAttrib else ''
                    tmp['trainer_id'] = int(trainerAttrib['id']) if 'id' in horseAttrib else -1

                    tmp['jockey_name'] = jockeyAttrib['name'] if 'name' in jockeyAttrib else ''
                    tmp['jockey_firstname'] = jockeyAttrib['firstname'] if 'firstname' in jockeyAttrib else ''
                    tmp['jockey_surname'] = jockeyAttrib['surname'] if 'surname' in jockeyAttrib else ''
                    tmp['jockey_id'] = int(jockeyAttrib['id']) if 'id' in jockeyAttrib else -1
                    tmp['jockey_riding_weight'] = float(jockeyAttrib['riding_weight']) if 'riding_weight' in jockeyAttrib and  len(jockeyAttrib['riding_weight'].strip()) > 0 else -1
                    tmp['jockey_apprentice_indicator'] = jockeyAttrib['apprentice_indicator'] if 'apprentice_indicator' in jockeyAttrib else ''

                    tmp['win_percentage'] = float(win_p.text) if win_p is not None else -1
                    tmp['place_percentage'] = float(place_p.text) if place_p is not None else -1

                    tmp['current_blinker_ind'] = horseCurrentBlinkerInd.text if horseCurrentBlinkerInd is not None else 'N'

                    if form.getchildren() is None: continue
                    for child in form.getchildren():
                        if child.tag == "meeting_date": tmp['date'] = datetime.strptime(child.text, "%d/%m/%Y")
                        if child.tag == "event_id": tmp['event_id'] = int(child.text)
                        if child.tag == "jockey":
                            jockey = child.attrib
                            tmp['jockey_name'] = jockey['name']
                            tmp['jockey_id'] = int(jockey['id'])
                        if child.tag == 'track':
                            track = child.attrib
                            tmp['track_name'] = track['name'].upper()
                            tmp['track_id'] = int(track['id'])
                            tmp['track_location'] = track['location']
                            tmp['track_condition'] = track['condition']
                            try:
                                tmp['track_grading'] = int(track['grading'])
                            except:
                                tmp['track_grading'] = -1
                            tmp['track_surface'] = track['track_surface'] if 'track_surface' in track else 'A'
                            tmp['track_3char_abbrev'] = track['track_3char_abbrev']
                            tmp['track_4char_abbrev'] = track['track_4char_abbrev']
                            tmp['track_6char_abbrev'] = track['track_6char_abbrev']
                        if child.tag == "race":
                            form_race = child.attrib
                            tmp['race_num'] = form_race['number']
                            tmp['race_name'] = form_race['name']
                        if child.tag == "starters":
                            tmp['starters'] = int(child.text)
                        if child.tag == "barrier":
                            tmp['barrier'] = int(child.text)
                        if child.tag == "weight_carried":
                            tmp['weight'] = float(child.text)
                        if child.tag == "positions":
                            positions = child.attrib
                            tmp['settling'] = int(positions['settling_down']) if 'settling_down' in positions else -1
                        if child.tag == "distance":
                            distance = child.attrib
                            tmp['distance'] = int(distance['metres'])
                        if child.tag == "sectional":
                            sectional = child.attrib
                            if sectional['distance'] == "600":
                                if ':' not in sectional['time']:
                                    t = sectional['time'].split(".")
                                    tmp['last_600'] = (float (t[2]) * 0.1 if len(t) > 2 else 0) + (float(t[1]) if len(t) > 1 else 0) + (60 * float(t[0]) if len(t) > 0 else 0)
                                else:
                                    t = sectional['time'].split (":")
                                    tmp['last_600'] = (float (t[1]) if len(t) > 1 else 0) + 60 * (float(t[0]) if len(t) > 0 else 0)
                        if child.tag == "finish_position":
                            try:
                                tmp['finish_number'] = int(child.text)
                            except:
                                tmp['finish_number'] = -1
                        if child.tag == "margin":
                            try:
                                tmp['margin'] = float(child.text)
                            except:
                                tmp['margin'] = -1
                        if child.tag == "event_duration":
                            if ':' not in child.text:
                                t = child.text.split(".")
                                tmp['time'] = (float (t[2]) * 0.1 if len(t) > 2 else 0) + (float(t[1]) if len(t) > 1 else 0) + (60 * float(t[0]) if len(t) > 0 else 0)
                            else:
                                t = child.text.split (":")
                                tmp['time'] = (float (t[1]) if len(t) > 1 else 0) + 60 * (float(t[0]) if len(t) > 0 else 0)
                        if child.tag == "event_prizemoney":
                            tmp['prizemoney_won'] = float(child.text)
                        if child.tag == "horse_prizemoney":
                            tmp['horse_prizemoney'] = float(child.text) if child.text is not None else -1
                        if child.tag == "horse_prizemoney_bonus":
                            tmp['horse_prizemoney_bonus'] = float(child.text) if child.text is not None else -1
                        if child.tag == "classes":
                            classId = child.find("class_id")
                            className = child.find("class")
                            tmp['class_id'] = int(classId.text) if classId is not None else -1
                            tmp['class'] = className.text if className is not None else ''
                    
                    if 'starters' in tmp and 'settling' in tmp:
                        if tmp['settling'] > 0:
                            tmp['settling'] = float("{:.2f}".format((tmp['starters'] - tmp['settling']) * 100 / (tmp['starters'] - 1)))
                        else:
                            tmp['settling'] = 0
                    if 'starters' in tmp and 'finish_number' in tmp:
                        if tmp['finish_number'] > 0:
                            if tmp['starters'] > 1:
                                tmp['finish_percentage'] = float("{:.2f}".format((tmp['starters'] - tmp['finish_number']) * 100 / (tmp['starters'] - 1)))
                            else:
                                tmp['finish_percentage'] = 0
                        else:
                            tmp['finish_percentage'] = -1
                    if 'distance' in tmp and 'time' in tmp and 'margin' in tmp:
                        if (tmp['time'] == 0): tmp['speed'] = 'INFINITY'
                        else:
                            tmp['time'] = float("{:.2f}".format((tmp['distance'] + tmp['margin'] * 2.4) * tmp['time'] /tmp['distance']))
                            tmp['speed'] = float("{:.2f}".format(tmp['distance'] / tmp['time']))

                    rlt.append (tmp)
            # tmpRace['horses'] = tmpHorses
            # btracks.append (tmpRace)
            # break
        # for horse in horses:

        # break
    return rlt, btracks
# if __name__ == "__main__":
#     main()
