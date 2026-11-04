from src.meteor.mrod_s3.mrod_s3_generator import parse_excel


def test_parse_excel_meteor_mrod_s3():
    filepath = 'D:\PycharmProjects\\flowgen-script\src\meteor\mrod_s3\input_data\input_data.xlsx'
    parse_excel(str(filepath))


print(test_parse_excel_meteor_mrod_s3())