import os
import PyPDF2
from datetime import datetime
import io

# ---------------------------------
# 전역 변수 설정 (필요에 맞게 수정)
# ---------------------------------
INPUT_FILE_PATH = 'resources/YOUR_PDF_FILE'  # 분할할 PDF 파일 경로 (/resources 디렉토리 내)
FILE_SPLIT_SIZE_MB = 20  # 분할 기준 파일 사이즈 (메가바이트 단위)
TITLE_INPUT = "SAVE_PDF_NAME"  # 저장할 파일 제목 (빈 문자열이면 기본명+실행일시)


# ---------------------------------

def split_pdf_by_size(pdf_file, size_threshold_mb):
    """
    pdf_file: 파일 객체 (rb 모드로 열린 PDF 파일)
    size_threshold_mb: 각 분할 파일의 최대 크기(메가바이트 단위)

    PDF 파일의 페이지들을 순차적으로 추가하면서, 생성된 PDF 파일의 크기가
    size_threshold_mb를 초과하면 해당 부분을 하나의 세그먼트로 분할합니다.
    분할은 페이지 단위로 이루어지므로 페이지 중간에서 내용이 잘리지 않습니다.

    Returns: (segments, total_pages)
      segments: [(segment_number, BytesIO객체, 시작페이지, 끝페이지), ...]
      total_pages: 전체 페이지 수
    """
    size_threshold_bytes = size_threshold_mb * 1024 * 1024
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)

    segments = []
    current_writer = PyPDF2.PdfWriter()
    current_segment_start_page = 1
    segment_number = 1

    for i in range(total_pages):
        current_writer.add_page(pdf_reader.pages[i])
        # 임시로 현재까지의 PDF를 BytesIO에 기록하여 크기 측정
        temp_output = io.BytesIO()
        current_writer.write(temp_output)
        current_size = temp_output.tell()

        # 지정 사이즈를 초과하면, 현재 세그먼트를 분할 파일로 확정
        if current_size >= size_threshold_bytes:
            temp_output.seek(0)
            segments.append((segment_number, temp_output, current_segment_start_page, i + 1))
            segment_number += 1
            # 새로운 분할을 위해 PdfWriter를 재생성
            current_writer = PyPDF2.PdfWriter()
            current_segment_start_page = i + 2  # 다음 페이지부터 새로운 세그먼트 시작

    # 남은 페이지가 있다면 마지막 분할 파일로 저장
    if len(current_writer.pages) > 0:
        temp_output = io.BytesIO()
        current_writer.write(temp_output)
        temp_output.seek(0)
        segments.append((segment_number, temp_output, current_segment_start_page, total_pages))

    return segments, total_pages


def generate_filename(title_input, segment_number):
    """
    제목 입력값이 없으면 원본 파일명 대신 실행 일시를 포함한 기본명 생성.
    입력값이 있으면 해당 제목 뒤에 '_'와 분할 번호를 붙여 파일명을 구성합니다.
    """
    if title_input.strip() == "":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"output_{timestamp}"
    else:
        base_name = title_input.strip()
    return f"{base_name}_{segment_number}.pdf"


def main():
    # 입력 파일 존재 여부 확인
    if not os.path.exists(INPUT_FILE_PATH):
        print(f"입력 파일이 존재하지 않습니다: {INPUT_FILE_PATH}")
        return

    try:
        with open(INPUT_FILE_PATH, 'rb') as f:
            segments, total_pages = split_pdf_by_size(f, FILE_SPLIT_SIZE_MB)
        print(f"전체 페이지 수: {total_pages}")
        print(f"분할된 세그먼트 수: {len(segments)}")

        output_directory = "result"
        os.makedirs(output_directory, exist_ok=True)

        for seg in segments:
            segment_number, pdf_bytes, start_page, end_page = seg
            filename = generate_filename(TITLE_INPUT, segment_number)
            output_file_path = os.path.join(output_directory, filename)
            with open(output_file_path, 'wb') as out_f:
                out_f.write(pdf_bytes.read())
            print(f"세그먼트 {segment_number}: 페이지 {start_page} ~ {end_page} 저장 완료. 파일: {output_file_path}")

    except Exception as e:
        print(f"PDF 분할 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
