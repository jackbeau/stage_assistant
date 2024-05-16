import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import '../models/cue.dart'; 
import '../models/annotation.dart';
import '../models/tag.dart';
import '../models/cue_type.dart';

abstract class AnnotationToolBase {
  final bool twoActions;
  AnnotationToolBase(this.twoActions);

  Offset cursorOffset = const Offset(0, 0);

  Annotation? tap(PdfPage page, Offset coordinates);
  Annotation? tap2(PdfPage page, Offset coordinates, Annotation annotation);
}

class NewCue extends AnnotationToolBase {
  NewCue() : super(true);

  @override
  Annotation? tap(PdfPage page, Offset coordinates) {

    // Define some sample Tags
    var tags = [
      Tag(cue_name: "1", type: fs),
      Tag(cue_name: "3", type: vfx),
      Tag(cue_name: "5", type: vfx),
    ];

    CueLabel newCue = CueLabel(page: page.pageNumber, pos: coordinates, type: goType, tags: tags, note:"on clap");
    return newCue;
  }

  @override
  Annotation? tap2(PdfPage page, Offset coordinates, Annotation annotation) {
    // provide an existing label and add a connected marker cue
    if (annotation is CueLabel) {
      // Inherit types and tags from the first cue
      CueMarker newCue = CueMarker(page: page.pageNumber, pos: coordinates, label: annotation);
      return newCue;
    }
    return null;
  }
}
