from os.path import expandvars
from pathlib import Path
from Vision import (
    VNRecognizeTextRequest,
    VNRequestTextRecognitionLevelAccurate,
    VNImageRequestHandler,
)
from Quartz import CGImageSourceCreateWithURL, CGImageSourceCreateImageAtIndex
from CoreFoundation import NSURL


def convert(image_path: str, transcript_path: str):
    image_url = NSURL.fileURLWithPath_(image_path)
    image_source = CGImageSourceCreateWithURL(image_url, None)
    if image_source is None:
        print("Failed to create image source")
        return

    cg_image_ref = CGImageSourceCreateImageAtIndex(image_source, 0, None)
    if cg_image_ref is None:
        print("Failed to get CGImage from source")
        return

    request = VNRecognizeTextRequest.alloc().initWithCompletionHandler_(
        lambda req, err: handle_results(req.results(), err, transcript_path)
    )

    request.setRecognitionLanguages_(["en-GB"])
    request.setRecognitionLevel_(VNRequestTextRecognitionLevelAccurate)
    request.setUsesLanguageCorrection_(True)

    handler = VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image_ref, {})
    success, error = handler.performRequests_error_([request], None)
    if not success:
        print("Failed to perform OCR:", error)


def handle_results(results, error, transcript_path):
    if error:
        print("Error during OCR:", error)
        return

    transcript_lines = []
    for observation in results:
        candidates = observation.topCandidates_(1)
        if candidates and candidates[0]:
            transcript_lines.append(candidates[0].string())

    Path(transcript_path).parent.mkdir(parents=True, exist_ok=True)
    with open(transcript_path, "w") as file:
        file.write("\n".join(transcript_lines))
    print(f"Written {len(transcript_lines):>2} lines to: {transcript_path}")


def main():
    diary_dir = Path(expandvars("$DIARY_DIR"))
    pattern = "scanned/[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/scanned-*.*"
    matches = reversed(list(diary_dir.glob(pattern)))

    for scanned_path in matches:
        transcript_path = (
            str(scanned_path)
            .replace("scanned-", "transcript-")
            .replace("scanned/", "transcripts/")
            .replace(".png", ".md")
            .replace(".jpg", ".md")
        )

        if Path(transcript_path).exists():
            print(f"Skipping existing: {transcript_path}")
            continue

        convert(str(scanned_path), transcript_path)


if __name__ == "__main__":
    main()
