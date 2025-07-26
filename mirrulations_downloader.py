import os
from dotenv import load_dotenv
import click
import time
import datetime

load_dotenv() #So we can get our passwords from the .env file


def parse_years(year_str):
    years = []
    for item in year_str.split(','):
        if '-' in item:
            start, end = map(int, item.split('-'))
            years.extend(range(start, end + 1))
        else:
            years.append(int(item))
    return years


def print_and_run_command_array(command_array):

    print("Preparing to run:")
    for this_command in command_array:
        print(f"\t{this_command}")

    if click.confirm('Do you want to run these commands?', default=False):
        for this_command in command_array:
            print(f"Running:\t{this_command}")
            os.system(this_command)
    else:
        print("Not running. Goodbye.")
        exit()


def generate_include_patterns(agency_list, year_list, docket_list, included_file_types):
    """Generate include patterns for the new folder structure with derived-data and raw-data"""
    include_patterns = []
    
    # Handle specific dockets
    if len(docket_list) > 0:
        for this_docket in docket_list:
            # Extract agency from docket ID (format: AGENCY-YEAR-ID)
            docket_parts = this_docket.split('-')
            if len(docket_parts) >= 3:
                agency = docket_parts[0]
                
                for this_file_type in included_file_types:
                    # Add patterns for both derived-data and raw-data
                    include_patterns.append(f"/derived-data/{agency}/{this_docket}/**/{this_file_type}")
                    include_patterns.append(f"/raw-data/{agency}/{this_docket}/**/{this_file_type}")
        return include_patterns
    
    # Handle agency/year combinations
    for this_agency in agency_list:
        for this_year in year_list:
            for this_file_type in included_file_types:
                if this_year == '*':
                    # No year filter - match all dockets for this agency
                    if this_agency == '*':
                        # Match everything
                        include_patterns.append(f"/derived-data/**/{this_file_type}")
                        include_patterns.append(f"/raw-data/**/{this_file_type}")
                    else:
                        # Match all dockets for specific agency
                        include_patterns.append(f"/derived-data/{this_agency}/**/{this_file_type}")
                        include_patterns.append(f"/raw-data/{this_agency}/**/{this_file_type}")
                else:
                    # Year filter - match dockets with specific year in docketID
                    if this_agency == '*':
                        # Match all agencies for specific year
                        include_patterns.append(f"/derived-data/*/*-{this_year}-*/**/{this_file_type}")
                        include_patterns.append(f"/raw-data/*/*-{this_year}-*/**/{this_file_type}")
                    else:
                        # Match specific agency and year
                        include_patterns.append(f"/derived-data/{this_agency}/*-{this_year}-*/**/{this_file_type}")
                        include_patterns.append(f"/raw-data/{this_agency}/*-{this_year}-*/**/{this_file_type}")
    
    return include_patterns


@click.command()
@click.option('--agency', '-a', default='', help="Agency acronyms(s) separated by commas.")
@click.option('--year', '-y', default='', help="Year(s) or range(s) of years separated by commas or dash (e.g., 2010-2015).")
@click.option('--textonly', is_flag=True, help="Flag to indicate if textonly should be True.")
@click.option('--getall', is_flag=True, help="Download all agencies, all years. (WARNING: this could cost a few hundred dollars...)")
@click.option('--transfers', default='', help="How many rclone connections to run at the same time (default is 50)")
@click.option('--docket','-d', default='', help="Download a specific docket id")

def main(agency, year, docket, textonly, getall, transfers ):
    agency_list = [agency.strip() for agency in agency.split(',') if agency.strip()]
    docket_list =  [docket.strip() for docket in docket.split(',') if docket.strip()]
    
    if year:
        year_list = parse_years(year)
    else:
        year_list = []

    run_command(agency_list, year_list, docket_list, textonly, getall, transfers)

def run_command(agency_list, year_list, docket_list, textonly, getall, transfers):
    """A command to generate and run the rclone commands needed to download regulations data from the mirrulations project!"""

    start_time = time.time()

    #How many rclone transfers should we use? We need to figure it out before we build the arguments to rclone that we 
    #Will use on any future command
    transfers_to_use = 50
    if transfers:
        if(transfers.isnumeric()):
            transfers_to_use = transfers
        else:
            print("Non numeric value for transfers argument. confusion. exiting")
            exit()
    checkers_to_use = int(transfers_to_use) * 2

    #these are the rclone commands that we always use (removed --s3-requester-pays)
    always_flags = f"  --checkers {checkers_to_use} --transfers {transfers_to_use} --log-file 'rclone.log' -P "

    #tracks whether there is a limitation argument
    is_limited = False

    if getall:
        is_enough = True
    else:
        is_enough = False

    if len(agency_list) > 0:
        is_enough = True
        is_limited = True
    else:
        agency_list = [ '*' ]

    if len(year_list) > 0:
        is_enough = True
        is_limited = True
    else:
        year_list = [ '*' ]

    if len(docket_list) > 0:
        is_enough = True
        is_limited = True
    else:
        docket_list = []

    #All 'text only' means is that we are not doing the word documents, pdfs, etc etc.. we just want to the raw text files
    #these come in three flavors... 
    if not textonly:
        included_file_types = ['*']
    else:
        included_file_types = ['*.txt','*.json','*.htm']
        is_limited = True
        is_enough = True

    #we either need --getall or we need some other limitation
    #we are not just going to download everything without some indication that we should...
    if not is_enough:
        print("If you want to download everything.. pass in the --getall paramater and go to lunch!! \nOtherwise add the --help for a full list of options")
        exit()
    
    #A substantial part of our configuration is contained in rclone configuration file 
    #We need to make sure these exist! 
    dest_dir = os.getenv('MIRRULATIONS_DESTINATION_PATH')
    rclone_config_file = os.getenv('RCLONE_CONFIG_FILE')

    has_error = False

    if not os.path.exists(dest_dir):
        print(f"Error: {dest_dir} does not exist ")
        has_error = True

    if not os.path.isfile(rclone_config_file):
        print(f"Error: {rclone_config_file} is not found")
        has_error = True

    if has_error:
        print("Crashing due to errors")
        exit()

    #If we get here then we have the files we need to proceed.
    #Updated base path to work with new structure (removed mirrulations/ subdirectory)
    base_rclone_command = f"rclone copy myconfig: {dest_dir} --config {rclone_config_file} {always_flags}"

    if getall:
        if is_limited:
            print(f"You have entered --getall and a filter at the same time. I dont know what to do... so I am not going to do anything. Try --help")
            exit()
        else:
            #If we get here, then should simply download everything.
            #we just run the command with no modification with --include statements
            commands_to_run = [ base_rclone_command ]
            print_and_run_command_array(commands_to_run)
    else:
        #Here we are downloading some subset of the data.. which we will express with one or more --include statements to the rclone command
        include_patterns = generate_include_patterns(agency_list, year_list, docket_list, included_file_types)

        this_command = base_rclone_command
        for include_pattern in include_patterns:
            this_command += f" --include \"{include_pattern}\" "

        command_array = [ this_command ]
        print_and_run_command_array(command_array)

    #No matter if we are downloading a portion or everything..
    #We print out how long it took to run.
    end_time = time.time()

    elapsed_time = round(end_time - start_time)
    printable_elapsed_time = str(datetime.timedelta(seconds = elapsed_time))

    print(f"""
Process finished!
    Took {printable_elapsed_time} to finish ( {elapsed_time} seconds )

            """)


if __name__ == "__main__":
    main()
