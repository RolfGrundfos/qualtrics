from qualtrics_export import QualtricsExporter

def main():
    try:
        exporter = QualtricsExporter()

        print("Qualtrics EMS Survey Exporter")
        print("=" * 40)

        # Find EMS survey
        ems_survey = exporter.find_survey_by_name("EMS")

        if ems_survey:
            print(f"Found EMS survey: {ems_survey['name']}")
            print(f"Survey ID: {ems_survey['id']}")
            print("\nStarting export...")

            # Export to CSV
            success = exporter.export_survey_to_csv(
                ems_survey['id'],
                "EMS_survey_responses.csv"
            )

            if success:
                print("\n✅ EMS survey export completed successfully!")
                print("File saved as: EMS_survey_responses.csv")
            else:
                print("\n❌ EMS survey export failed!")

        else:
            print("❌ EMS survey not found!")
            print("Available surveys:")
            surveys = exporter.get_surveys()
            for survey in surveys[:10]:  # Show first 10 surveys
                print(f"  - {survey['name']} (ID: {survey['id']})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()