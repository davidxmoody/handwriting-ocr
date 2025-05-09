import sys
import Vision
from Quartz import CGImageSourceCreateWithURL, CGImageSourceCreateImageAtIndex
from CoreFoundation import NSURL


def main(image_path):
    image_url = NSURL.fileURLWithPath_(image_path)
    image_source = CGImageSourceCreateWithURL(image_url, None)
    if image_source is None:
        print("Failed to create image source")
        return

    cg_image_ref = CGImageSourceCreateImageAtIndex(image_source, 0, None)
    if cg_image_ref is None:
        print("Failed to get CGImage from source")
        return

    request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(
        lambda req, err: handle_results(req.results(), err)
    )

    request.setRecognitionLanguages_(["en-GB"])
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    request.setUsesLanguageCorrection_(True)

    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(
        cg_image_ref, {}
    )
    success, error = handler.performRequests_error_([request], None)
    if not success:
        print("Failed to perform OCR:", error)


def handle_results(results, error):
    if error:
        print("Error during OCR:", error)
        return
    for observation in results:
        candidates = observation.topCandidates_(1)
        if candidates and candidates[0]:
            print(candidates[0].string())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert.py input.png")
    else:
        main(sys.argv[1])
