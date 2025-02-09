/// Author: Jack Beaumont
/// Date: 06/06/2024
///
/// This file contains the CustomToolbar widget, which includes various UI elements
/// such as mode switcher, inspector switcher, and toolbar buttons for an app.
library;

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/bloc/app_bar_bloc.dart';
import '../../../domain/bloc/script_editor_bloc.dart';
import 'mode_switcher.dart';
import 'inspector_switcher.dart';
import '../../../../../core/constants/app_images.dart';

/// Helper class to handle icon creation with specific styles.
class IconHelper {
  /// Returns an Image widget with the given [assetPath], [isSelected] flag,
  /// and optional [width]. The icon color changes based on [isSelected].
  static Image getIcon(BuildContext context, String assetPath, bool isSelected,
      {double width = 20}) {
    return Image.asset(
      assetPath,
      color: isSelected
          ? Theme.of(context).colorScheme.primaryContainer
          : Theme.of(context).colorScheme.onSurface,
      width: width,
    );
  }
}

/// CustomToolbar is a StatelessWidget that provides a custom app bar with various tools and modes.
class CustomToolbar extends StatelessWidget {
  const CustomToolbar({super.key});

  @override
  Widget build(BuildContext context) {
    // Provide AppBarBloc to handle toolbar actions.
    return BlocProvider<AppBarBloc>(
      create: (context) => AppBarBloc(
          BlocProvider.of<ScriptEditorBloc>(context).state.pdfController!),
      child: BlocBuilder<ScriptEditorBloc, ScriptEditorState>(
        builder: (context, state) {
          final appBarBloc = BlocProvider.of<AppBarBloc>(context);
          final screenWidth = MediaQuery.of(context).size.width;
          final Mode currentMode = state.mode;
          final InspectorPanel selectedInspector = state.selectedInspector;
          final bool isCameraActive = state.isCameraVisible;
          final Tool selectedTool = state.selectedTool;

          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            height: 52,
            color: Theme.of(context).colorScheme.surface,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  flex: 2,
                  child: Row(
                    children: [
                      SizedBox(
                        width: 180,
                        child: ModeSwitcher(currentMode: currentMode),
                      ),
                      const SizedBox(width: 12),
                      if (currentMode == Mode.edit)
                        IconButton(
                          icon: IconHelper.getIcon(context, ThemeIcons.cueTool,
                              selectedTool == Tool.newCue,
                              width: 24),
                          onPressed: () =>
                              BlocProvider.of<ScriptEditorBloc>(context).add(
                                  ToolChanged(selectedTool == Tool.newCue
                                      ? Tool.none
                                      : Tool.newCue)),
                          tooltip: "Add cue",
                        ),
                    ],
                  ),
                ),
                if (screenWidth >= 1080)
                  Expanded(
                    flex: 1,
                    child: Center(
                      child: Text(
                        "Romeo and Juliet",
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                    ),
                  ),
                Expanded(
                  flex: 2,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      IconButton(
                        icon: Icon(Icons.search,
                            color: Theme.of(context).colorScheme.onSurface),
                        onPressed: () {},
                      ),
                      IconButton(
                        icon: Icon(Icons.zoom_out,
                            color: Theme.of(context).colorScheme.onSurface),
                        onPressed: () => appBarBloc.add(ZoomOut()),
                      ),
                      IconButton(
                        icon: Icon(Icons.zoom_in,
                            color: Theme.of(context).colorScheme.onSurface),
                        onPressed: () => appBarBloc.add(ZoomIn()),
                      ),
                      const SizedBox(width: 12),
                      IconButton(
                        icon: IconHelper.getIcon(
                            context, ThemeIcons.camera, isCameraActive),
                        onPressed: () {
                          BlocProvider.of<ScriptEditorBloc>(context)
                              .add(ToggleCameraView());
                        },
                        tooltip: "Show stage camera",
                      ),
                      const SizedBox(width: 8),
                      SizedBox(
                        width: 220,
                        child: InspectorSwitcher(
                            selectedInspector: selectedInspector),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
