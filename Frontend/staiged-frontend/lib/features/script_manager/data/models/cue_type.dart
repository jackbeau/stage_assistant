import 'package:flutter/material.dart';

class CueType {
  final String text;
  final Color color;
  String side;

  CueType(this.text, this.color, this.side){
    // Validate the side parameter to ensure it's either 'l' or 'r'
    assert(side == 'l' || side == 'r', "Side must be 'l' (left) or 'r' (right)");
  }
}

var standbyType = CueType(
  "STANDBY",
  const Color.fromARGB(255, 122, 125, 142),
  "l"
);

var goType = CueType(
  "GO",
  const Color.fromARGB(255, 32, 34, 46),
  "r"
);
