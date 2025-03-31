import os
import PyPDF2
from datetime import datetime
import io

# ----------------------
# 설정 (사용자가 필요에 맞게 수정)
# ----------------------
INPUT_FILE_PATH = 'resources/YOUR_PDF_FILE'  # 자를 PDF 파일 경로 (resources 디렉토리 내)
START_PAGE = 1  # 시작 페이지 번호 (1부터 시작)
END_PAGE = 1  # 끝 페이지 번호 (해당 포함)
TITLE_INPUT = "SAVE_PDF_NAME"  # 저장할 파일 제목 (미입력 시 원본 파일명+실행일시 사용)


# ----------------------

def split_pdf(pdf_file, start_page, end_page):
    """
    PDF 파일 객체에서 지정한 시작 페이지부터 끝 페이지까지의 내용을 추출하여
    새로운 PDF 파일 객체(BytesIO)를 생성합니다.
    (페이지 번호는 1부터 시작, 내부적으로는 0-indexed로 처리)
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    pdf_writer = PyPDF2.PdfWriter()
    for i in range(start_page - 1, end_page):
        pdf_writer.add_page(pdf_reader.pages[i])
    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)
    return output


def generate_filename(input_file_path, title_input):
    """
    제목 입력값이 없을 경우, 원본 파일명과 실행 일시를 결합하여 저장 파일명을 생성합니다.
    입력값이 있을 경우 해당 제목에 ".pdf"를 붙여 파일명을 구성합니다.
    """
    if title_input.strip() == "":
        original_name = os.path.basename(input_file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{os.path.splitext(original_name)[0]}_{timestamp}.pdf"
    else:
        filename = title_input.strip() + ".pdf"
    return filename


def main():
    if not os.path.exists(INPUT_FILE_PATH):
        print(f"입력 파일이 존재하지 않습니다: {INPUT_FILE_PATH}")
        return

    try:
        with open(INPUT_FILE_PATH, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
        print(f"입력 파일의 총 페이지 수: {total_pages}")
    except Exception as e:
        print(f"PDF 파일 읽기 오류: {e}")
        return

    if START_PAGE > END_PAGE or END_PAGE > total_pages:
        print("유효하지 않은 페이지 범위입니다. 페이지 번호를 다시 확인해주세요.")
        return

    try:
        with open(INPUT_FILE_PATH, 'rb') as f:
            output_pdf = split_pdf(f, START_PAGE, END_PAGE)
        filename = generate_filename(INPUT_FILE_PATH, TITLE_INPUT)

        output_directory = "results/"
        os.makedirs(output_directory, exist_ok=True)
        output_file_path = os.path.join(output_directory, filename)

        with open(output_file_path, 'wb') as out_f:
            out_f.write(output_pdf.read())

        print(f"PDF 분할이 완료되었습니다. 파일 저장: {output_file_path}")
    except Exception as e:
        print(f"PDF 분할 중 오류 발생: {e}")


if __name__ == "__main__":
    main()