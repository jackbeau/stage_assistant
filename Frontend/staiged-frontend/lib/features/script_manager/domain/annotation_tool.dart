import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'cue.dart'; 
import '../data/models/annotation.dart';
import '../data/models/tag.dart';
import '../data/models/cue_type.dart';
import 'cue_marker.dart';

abstract class AnnotationToolBase {
  final bool twoActions;
  AnnotationToolBase(this.twoActions);

  Offset cursorOffset = const Offset(0, 0);

  tap(PdfPage page, Offset coordinates, List<Annotation> annotations) {}
  void tap2(PdfPage page, Offset coordinates, List<Annotation> annotations, Annotation annotation) {}
  void down(PdfPage page, Offset cursorPos, Annotation annotation) {}
  void move(Offset delta, Annotation annotation, {PdfPage? page, PdfViewerController? controller}) {}
}

class NewCue extends AnnotationToolBase {
  NewCue() : super(true);

  @override
  tap(PdfPage page, Offset coordinates, List<Annotation> annotations) {
    // Define a new CueType for demonstration

    // Define some sample Tags
    var tags = [
      Tag(cue_name: "1", type: fs),
      Tag(cue_name: "3", type: vfx),
      Tag(cue_name: "5", type: vfx),
    ];

    Cue newCue = Cue(page: page.pageNumber, pos: coordinates, type: goType, tags: tags, note:"on clap");
    annotations.add(newCue);
    return newCue;
  }

  @override
  void tap2(PdfPage page, Offset coordinates, List<Annotation> annotations, Annotation annotation) {
    if (annotation is Cue) {
      // Inherit types and tags from the first cue
      CueMarker newCue = CueMarker(page: page.pageNumber, pos: coordinates, type: annotation.type, tags: annotation.tags, label: annotation);
      annotations.add(newCue);
    }
  }
}
