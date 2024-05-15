import 'package:flutter_bloc/flutter_bloc.dart';
import '../cue.dart'; // Update this path to the actual location of your Cue model.
import '../../data/models/tag.dart'; // Update this path to the actual location of your Cue model.

// Event definitions
abstract class CueEditorEvent {}
class LoadCue extends CueEditorEvent {
  final Cue? cue;
  LoadCue(this.cue);
}
class AddTag extends CueEditorEvent {
  final Tag tag;
  AddTag(this.tag);
}
class RemoveTag extends CueEditorEvent {
  final int index;
  RemoveTag(this.index);
}
class UpdateTag extends CueEditorEvent {
  final int index;
  final Tag updatedTag;
  UpdateTag(this.index, this.updatedTag);
}
class CueFieldUpdated extends CueEditorEvent {
  final String field;
  final dynamic value;
  CueFieldUpdated(this.field, this.value);
}
class SubmitCue extends CueEditorEvent {}

// State definitions
abstract class CueEditorState {}
class CueEditorInitial extends CueEditorState {}
class CueEditorLoading extends CueEditorState {}
class CueEditorSuccess extends CueEditorState {
  final Cue? cue;
  CueEditorSuccess(this.cue);
}
class CueEditorError extends CueEditorState {
  final String error;
  CueEditorError(this.error);
}

// BLoC definition
class CueEditorBloc extends Bloc<CueEditorEvent, CueEditorState> {
  Cue? cueDraft;

  CueEditorBloc() : super(CueEditorInitial()) {

    on<LoadCue>((event, emit) {
      cueDraft = event.cue;
      if (cueDraft != null) {
      emit(CueEditorSuccess(cueDraft!));  // Emit success with the loaded cue
      }

    });

    on<AddTag>((event, emit) {
      if (cueDraft == null) return;
      cueDraft!.tags.add(event.tag);
      emit(CueEditorSuccess(cueDraft!));
    });

    on<RemoveTag>((event, emit) {
      if (cueDraft == null) return;
      cueDraft!.tags.removeAt(event.index);
      emit(CueEditorSuccess(cueDraft!));
    });

    on<UpdateTag>((event, emit) {
      if (cueDraft == null) return;
      cueDraft!.tags[event.index] = event.updatedTag;
      emit(CueEditorSuccess(cueDraft!));
    });
    
    on<CueFieldUpdated>((event, emit) {
      if (cueDraft == null) {
        emit(CueEditorError('No cue loaded to update'));
        return;
      }
      print(event.value);
      final updatedCue = applyFieldUpdate(cueDraft!, event.field, event.value);
      emit(CueEditorSuccess(cueDraft!)); // Emit success with updated draft
      // Todo, sent to network and update UI
    });

    // on<SubmitCue>(async (event, emit) {
    //   emit(CueEditorLoading());
    //   try {
    //     // Simulate sending data to the server or use an actual repository method
    //     // Assuming success if no exceptions
    //     emit(CueEditorSuccess(cueDraft));
    //   } catch (e) {
    //     emit(CueEditorError(e.toString()));
    //   }
    // });
  }

  Cue applyFieldUpdate(Cue cue, String field, dynamic value) {
    switch (field) {
      case 'tags':
        return cue.copyWith(tags: value as List<Tag>);
      case 'note':
        return cue.copyWith(note: value as String);
      case 'title':
        return cue.copyWith(title: value as String);
      case 'autofire':
        return cue.copyWith(autofire: value as bool);
      case 'line':
        return cue.copyWith(line: value as String);
      case 'message':
        return cue.copyWith(message: value as String);
      default:
        return cue; // No field matched
    }
  }
}
