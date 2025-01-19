import pandas as pd
import json

# Load the Excel file and stripping extra spaces
excel_file_path = "SJRP1Atest2rows.xlsx" 
df = pd.read_excel(excel_file_path)
df.columns = df.columns.str.strip()

# [1] Filter out columns that have date value and change the format from dd/mm/yyyy to yyyymmdd.
#==============================================================================================
columns_with_date = ['Enrolment Date','Year of birth of the child', 'FM Start Date of enrolment','CCFA Start Date','CCFA End Date']

# Filter columns out only selected columns that have date values in them
datecolumns_df = df[columns_with_date]

# Change date format from dd/mm/yyyy to yyyymmdd
for col in datecolumns_df:
    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y%m%d')

#==============================================================================================


# [2] Update "Salaried Employee" to WEP, "Self Employed" to WSP, "Salaried Employee & Self Employed" to WEPWSP else, NW
#==============================================================================================
def map_working_status(status):
    if status == "Salaried Employee":
        return "WEP"
    elif status == "Self Employed":
        return "WSP"
    elif status == "Salaried Employee & Self Employed":
        return "WEPWSP"
    else:
        return "NW"

df['Main Applicant working status'] = df['Main Applicant working status'].apply(map_working_status)
#==============================================================================================


# Define mappings between Excel columns and JSON fields
column_to_json_mapping = {
    
    #Child Info
    "":"ChildInfo.Gender",  
    "Year of birth of the child" :"ChildInfo.DateOfBirth",  
    "Child ID":"ChildInfo.IdentityNumber",  
    "Child ID Type":"ChildInfo.IdentityType",  
    "":"ChildInfo.Name",  
    "":"ChildInfo.Race",  
    "":"ChildInfo.RelationshipToChild",  
    "Child Citizenship":"ChildInfo.TypeOfCitizenship",  
    
    #Main Applicant Info
    "Main Applicant Relationship to Child":"EnrolmentApplicantInfo.RelationshipToChild",
    "LG Specific Relationship":"EnrolmentApplicantInfo.SpecificRelationship",
    "":"EnrolmentApplicantInfo.Name",
    "":"EnrolmentApplicantInfo.Gender",
    "Year of birth of Applicant":"EnrolmentApplicantInfo.DateOfBirth",
    "":"EnrolmentApplicantInfo.TypeOfCitizenship",
    "Applicant ID":"EnrolmentApplicantInfo.IdentityNumber",
    "Main Applicant ID Type":"EnrolmentApplicantInfo.IdentityType",
    "Main Applicant":"EnrolmentApplicantInfo.MaritalStatus",
    "":"EnrolmentApplicantInfo.IsJointCustody",
    "":"EnrolmentApplicantInfo.PostalCode",
    "":"EnrolmentApplicantInfo.BlockNumber",
    "":"EnrolmentApplicantInfo.StreetName",
    "":"EnrolmentApplicantInfo.BuildingName",
    "":"EnrolmentApplicantInfo.FloorNo",
    "":"EnrolmentApplicantInfo.UnitNo",
    "Main Applicant working status":"EnrolmentApplicantInfo.WorkingStatus",
    "Main Applicant Not working reason":"EnrolmentApplicantInfo.NWReason",
    "":"EnrolmentApplicantInfo.ApplicantWSG",
    "":"EnrolmentApplicantInfo.EDD",
    "Within last 2 months":"EnrolmentApplicantInfo.EmploymentWithInPast2Months",
    "Main Applicant Emp start Date":"EnrolmentApplicantInfo.DateOfEmployment",
    "Main Applicant - Receiving CPF ?":"EnrolmentApplicantInfo.ReceivingCPF",
    "Main Applicant Gross Monthly Income 1":"EnrolmentApplicantInfo.MainApplicantWEPGrossMonthlyIncome",
    "Main Applicant has NOA ?":"EnrolmentApplicantInfo.HasLatestNOA",
    "Main Applicant Gross Monthly Income 1":"EnrolmentApplicantInfo.MainApplicantWSPGrossMonthlyIncome",
    "":"EnrolmentApplicantInfo.MobileNoSG",
    "":"EnrolmentApplicantInfo.TelephoneNo",
    "":"EnrolmentApplicantInfo.EmailAddress",

    #Enrolment Info
    "":"EnrolmentInfo.EnrolmentID",
    "":"EnrolmentInfo.DateOfEnrolment",
    "":"EnrolmentInfo.EnlmMthProgFeeWOGST",
    "":"EnrolmentInfo.EnlmMthProration",
    "":"EnrolmentInfo.AppliedForPCI",
    "":"EnrolmentInfo.CCFAInfo",
    "":"EnrolmentInfo.CCFARequired",
    "":"EnrolmentInfo.TypeOfReferral",
    "":"EnrolmentInfo.CCFANonWorkingReasons",
    "":"EnrolmentInfo.OtherDescription",
    "":"EnrolmentInfo.ReferralBy",
    "":"EnrolmentInfo.NameOfAgency",
    "":"EnrolmentInfo.SocialWorkerName",
    "":"EnrolmentInfo.SocialWorkerEmail",
    "":"EnrolmentInfo.RecommendedCopayment",
    "":"EnrolmentInfo.StartDate",
    "":"EnrolmentInfo.MonthsRequired",
    "":"EnrolmentInfo.EndDate",
    "":"EnrolmentInfo.CCFASUG",
    "":"EnrolmentInfo.CCSUGRequired",
    "":"EnrolmentInfo.IsDeclarationSelected",
    "":"EnrolmentInfo.Declaration",

    #Family Member List
    "":"FamilyMemberList.Name",
    "":"FamilyMemberList.RelationshipToChild",
    "":"FamilyMemberList.IdentityNumber",
    "":"FamilyMemberList.DateOfBirth",
    "":"FamilyMemberList.WorkingStatus",
    "":"FamilyMemberList.GrossMonthlyIncome",
    "":"FamilyMemberList.EmploymentWithInPast2Months",
    "":"FamilyMemberList.DateOfEmployment",
    "":"FamilyMemberList.Consent",
    "":"FamilyMemberList.IsNoValidAuthority",
    "":"FamilyMemberList.ConsentScope",
    "":"FamilyMemberList.ConsentType",
    "":"FamilyMemberList.ConsentSigningDate",
    "":"FamilyMemberList.ConsentProviders",

    #Spouse Info
    "":"SpouseInfo.RelationshipToChild",
    "":"SpouseInfo.SpecificRelationship",
    "":"SpouseInfo.Name",
    "":"SpouseInfo.DateOfBirth",
    "":"SpouseInfo.Gender",
    "":"SpouseInfo.TypeOfCitizenship",
    "Spouse ID":"SpouseInfo.IdentityNumber",
    "":"SpouseInfo.IdentityType",
    "":"SpouseInfo.IsIncarcerated",
    "":"SpouseInfo.IsMentallyIncapacitated",
    "":"SpouseInfo.WorkingStatus",
    "":"SpouseInfo.DateOfEmployment",
    "":"SpouseInfo.EmploymentWithInPast2Months",
    "":"SpouseInfo.DateOfEmployment",
    "":"SpouseInfo.SpouseReceivingCPF",
    "":"SpouseInfo.SpouseWEPGrossMonthlyIncome",
    "":"SpouseInfo.SpouseHasLatestNOA",
    "":"SpouseInfo.SpouseWSPGrossMonthlyIncome",
    "":"SpouseInfo.MobileNoSG",
    "":"SpouseInfo.TelephoneNo",
    "":"SpouseInfo.EmailAddress",
    "":"SpouseInfo.Consent",
    "":"SpouseInfo.IsNoValidAuthority",
    "":"SpouseInfo.ConsentScope",
    "":"SpouseInfo.ConsentType",
    "":"SpouseInfo.ConsentSigningDate",

    "":"ApplicationStatus.StatusCode",
    "":"ApplicationStatus.RejectionCode",
    "":"ApplicationStatus.RejectionDescription",

    "":"DocumentCategoryList.Code",
    "":"DocumentCategoryList.FileName",
}
num = 1
# Replace missing values with blanks
df = df.fillna("")
# Build the JSON data
json_data = []
for _, row in df.iterrows():
    row_json = {
        f"Row {num}"
        "ChildInfo": {
            "Gender":row.get("",""),
            "DateOfBirth":row.get("Year of birth of the child",""),
            "IdentityNumber": row.get("Child ID", ""),
            "IdentityType": row.get("Child ID Type", ""),
            "Name":row.get("",""),
            "Race":row.get("",""),
            "RelationshipToChild":"Child",
            "TypeOfCitizenship":row.get("Child Citizenship",""),
            
        },
        "EnrolmentApplicantInfo": {
            "RelationshipToChild": row.get("Main Applicant Relationship to Child",""),
            "SpecificRelationship": row.get("LG Specific Relationship",""),
            "Name": row.get("",""),
            "Gender": row.get("",""),
            "DateOfBirth": row.get("Year of birth of Applicant",""),
            "TypeOfCitizenship": row.get("",""),
            "IdentityNumber": row.get("Applicant ID",""),
            "IdentityType": row.get("Main Applicant ID Type",""),
            "MaritalStatus": row.get("Main Applicant",""),
            "IsJointCustody": row.get("",""),
            "PostalCode": row.get("",""),
            "BlockNumber": row.get("",""),
            "StreetName": row.get("",""),
            "BuildingName": row.get("",""),
            "FloorNo": row.get("",""),
            "UnitNo": row.get("",""),
            "WorkingStatus": [{"Value" : row.get("Main Applicant working status","")}],
            "NWReason": row.get("Main Applicant Not working reason",""),
            "ApplicantWSG": row.get("",""),
            "EDD": row.get("",""),
            "EmploymentWithInPast2Months": row.get("Within last 2 months",""),
            "DateOfEmployment": row.get("Main Applicant Emp start Date",""),
            "ReceivingCPF":row.get("Main Applicant - Receiving CPF ?",""),
            "MainApplicantWEPGrossMonthlyIncome": row.get("Main Applicant Gross Monthly Income 1",""),
            "HasLatestNOA": row.get("Main Applicant has NOA ?",""),
            "MainApplicantWSPGrossMonthlyIncome": row.get("Main Applicant Gross Monthly Income 1",""),
            "MobileNoSG": "69000003",
            "TelephoneNo": "89000003",
            "EmailAddress": "izdihar.zuraimi@ncs.com.sg",
            "Consent": {
                "IsNoValidAuthority": "N",
                "ConsentScope": "AS",
                "ConsentType": "NCO",
                "ConsentSigningDate": "20240930",
                }
        },
        "EnrolmentInfo":{
            "DateOfEnrolment": row.get("", ""),
            "EnlmMthProgFeeWOGST": row.get("", ""),
            "EnlmMthProration": row.get("", ""),
            "AppliedForPCI": row.get("", ""),
            "CCFAInfo": {
                "CCFARequired": row.get("", ""),
                "TypeOfReferral": row.get("", ""),
                "CCFANonWorkingReasons": row.get("", ""),
                "OtherDescription": row.get("", ""),
                "ReferralBy": row.get("", ""),
                "NameOfAgency": row.get("", ""),
                "SocialWorkerName": row.get("", ""),
                "SocialWorkerEmail": row.get("", ""),
                "RecommendedCopayment": row.get("", ""),
                "StartDate": row.get("", ""),
                "MonthsRequired": row.get("", ""),
                "EndDate": row.get("", "")
            },
            "CCFASUG": {
                "CCSUGRequired": row.get("", ""),
            },
            "IsDeclarationSelected": row.get("", ""),
            "Declaration": [
                {
                    "Display": "Exact declaration pending ECDA confirmation."
                }
            ]
        },

        "FamilyMemberList": [
            {
                "Name": row.get("", ""),
                "RelationshipToChild": row.get("", ""),
                "IdentityNumber": row.get("", ""),
                "DateOfBirth": row.get("", ""),
                "WorkingStatus": row.get("", ""),
                "GrossMonthlyIncome": row.get("", ""),
                "EmploymentWithInPast2Months": row.get("", ""),
                "DateOfEmployment": row.get("", ""),
                "Consent": {
                    "IsNoValidAuthority": "N",
                    "ConsentScope": "AS",
                    "ConsentType": "NCO",
                    "ConsentSigningDate": "20240930",
                }
            },
            {
                "Name": row.get("", ""),
                "RelationshipToChild": row.get("", ""),
                "IdentityNumber": row.get("", ""),
                "DateOfBirth": row.get("", ""),
                "WorkingStatus": row.get("", ""),
                "GrossMonthlyIncome": row.get("", ""),
                "EmploymentWithInPast2Months": row.get("", ""),
                "DateOfEmployment": row.get("", ""),
                "Consent": {
                    "IsNoValidAuthority": "N",
                    "ConsentScope": "AS",
                    "ConsentType": "NCO",
                    "ConsentSigningDate": "20240930",
                }
            },
            {
                "Name": row.get("", ""),
                "RelationshipToChild": row.get("", ""),
                "IdentityNumber": row.get("", ""),
                "DateOfBirth": row.get("", ""),
                "WorkingStatus": row.get("", ""),
                "GrossMonthlyIncome": row.get("", ""),
                "EmploymentWithInPast2Months": row.get("", ""),
                "DateOfEmployment": row.get("", ""),
                "Consent": {
                    "IsNoValidAuthority": row.get("", ""),
                    "ConsentScope": row.get("", ""),
                    "ConsentType": row.get("", ""),
                    "ConsentSigningDate": row.get("", ""),
                    "ConsentProviders": [
                    {
                        "IdentityNumber": row.get("", ""),
                        "IdentityType": row.get("", ""),
                        "Name": row.get("", ""),
                        "LegalCapacity": row.get("", ""),
                        "ConsentSigningDate": row.get("", ""),
                    }
                ]
                },
            },

        ],

        "SpouseInfo": {
            "RelationshipToChild": row.get("", ""),
            "SpecificRelationship": row.get("", ""),
            "Name": row.get("", ""),
            "DateOfBirth": row.get("", ""),
            "Gender": row.get("", ""),
            "TypeOfCitizenship": row.get("", ""),
            "IdentityNumber": row.get("Spouse ID", ""),
            "IdentityType": row.get("", ""),
            "IsIncarcerated": row.get("", ""),
            "IsMentallyIncapacitated": row.get("", ""),
            "WorkingStatus": row.get("", ""),
            "DateOfEmployment": row.get("", ""),
            "EmploymentWithInPast2Months": row.get("", ""),
            "SpouseReceivingCPF": row.get("", ""),
            "SpouseWEPGrossMonthlyIncome": row.get("", ""),
            "SpouseHasLatestNOA": row.get("", ""),
            "SpouseWSPGrossMonthlyIncome": row.get("", ""),
            "MobileNoSG": row.get("", ""),
            "TelephoneNo": row.get("", ""),
            "EmailAddress": row.get("", ""),
            "Consent": {
                "IsNoValidAuthority": "N",
                "ConsentScope": "AS",
                "ConsentType": "NCO",
                "ConsentSigningDate": "20240930",
                }
        },
        "ApplicationStatus": {
            "StatusCode": "00",
            "RejectionCode": "",
            "RejectionDescription": ""
        },
        "DocumentCategoryList": [
        {
            "Code": "SPDNW",
            "FileName": "SPDNW.doc"
        },
        {
            "Code": "",
            "FileName": ""
        }
        ]
    }

    json_data.append(f"Row {num}, TC00{num}")
    num = num + 1
    
    json_data.append(row_json)

# Save the JSON data to a file
json_file_path = "output_data.json"
with open(json_file_path, "w") as json_file:
    json.dump(json_data, json_file, indent=4)

print(f"Custom JSON has been saved to {json_file_path}")