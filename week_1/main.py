import sys
from pathlib import Path # Figure out why use Path?
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import run_data_profile

SOURCE_DIR = Path("week_1/data/0_source")
BRONZE_DIR = Path("week_1/data/1_bronze")
SILVER_DIR = Path("week_1/data/2_silver")
GOLD_DIR = Path("week_1/data/3_gold")
DB_NAME = "jobs.db"

#print("🔥 MAIN.PY IS RUNNING")

def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    ingest_all_mhtml(input_dir, output_dir)

def run_silver():
    input_dir = BRONZE_DIR
    output_dir = SILVER_DIR
    process_all_html(input_dir, output_dir)

def run_gold():
    input_dir = SILVER_DIR
    output_dir = GOLD_DIR
    load_all_jsons(input_dir, output_dir)

def run_profiler():
    db_path = GOLD_DIR / DB_NAME
    run_data_profile(db_path)

def run_all():

    print("\n========== FULL PIPELINE START ==========\n")

    run_bronze()
    run_silver()
    run_gold()
    run_profiler()

    print("\n========== PIPELINE COMPLETE ==========\n")


#def main():
	# ORCHESTRATION TO BE IMPLEMENTED HERE

        #print("COMMAND:", command)

       # if len(sys.argv) < 2:
          #  print("Usage: python main.py [ingest|silver|gold|profile]")
         #   return

        #command = sys.argv[1]

        #match command:
           # case "ingest":
          #      print("🚀 RUN BRONZE CALLED")
         #       run_bronze()

        #    case "silver":
       #         run_silver()

      #      case "gold":
     #           run_gold()

    #        case "profile":
   #             run_profiler()

  #          case _:
 #               print("Unknown command:", command)
#                print("Available commands: ingest, silver, gold, profile")


def main():

    if len(sys.argv) < 2:
    
        print(
            "Usage: python main.py "
            "[ingest|process|load|profile|all]"
        )

        print("\nCommand set:")
        print("python week_1/main.py ingest")
        print("python week_1/main.py process")
        print("python week_1/main.py load")
        print("python week_1/main.py profile")
        print("python week_1/main.py all")

        return

    command = sys.argv[1]

    if command == "ingest":
        #print("🚀 ENTERING INGEST MODE")
        run_bronze()

    elif command == "process":
        #print("SILVER MODE")
        run_silver()

    elif command == "load":
        #print("🥇 ENTERING GOLD MODE")
        run_gold()

    elif command == "profile":
        run_profiler()
    
    elif command == "all":
        run_all()

    else:
        print("❌ UNKNOWN COMMAND:", command)

   # print("ARGS:", sys.argv)

    #if len(sys.argv) < 2:
      #  print("No command given")
     #   return

    #command = sys.argv[1]
    #print("COMMAND:", command)

   # if command == "ingest":
     #   print("🚀 RUN BRONZE CALLED")
    #    run_bronze()

   # else:
  #      print("Unknown command:", command)

if __name__ == "__main__":
    main()