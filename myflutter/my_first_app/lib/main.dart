import 'package:flutter/material.dart';
import 'dart:math' as math;
import 'package:math_expressions/math_expressions.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Scientific Calculator',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const CalculatorPage(title: 'Scientific Calculator'),
    );
  }
}

class CalculatorPage extends StatefulWidget {
  const CalculatorPage({super.key, required this.title});
  final String title;

  @override
  State<CalculatorPage> createState() => _CalculatorPageState();
}

class _CalculatorPageState extends State<CalculatorPage> {
  String _expression = '';
  String _result = '';
  TextEditingController _inputController = TextEditingController();
  FocusNode _inputFocusNode = FocusNode();

  @override
  void dispose() {
    _inputController.dispose();
    _inputFocusNode.dispose();
    super.dispose();
  }

  void _onButtonPressed(String value) {
    if (value == 'AC') {
      setState(() {
        _expression = '';
        _result = '';
        _inputController.text = '';
      });
    } else if (value == '⌫') {
      setState(() {
        if (_inputController.text.isNotEmpty) {
          final selection = _inputController.selection;
          final text = _inputController.text;
          if (selection.start > 0) {
            final newText = text.replaceRange(selection.start - 1, selection.start, '');
            _inputController.text = newText;
            _inputController.selection = TextSelection.collapsed(offset: selection.start - 1);
          }
        }
        _expression = _inputController.text;
      });
    } else if (value == '=') {
      setState(() {
        try {
          _result = _evaluate(_inputController.text);
        } catch (e) {
          _result = 'Error';
        }
      });
    } else if (value == 'BMI') {
      _showBmiDialog();
    } else {
      setState(() {
        final selection = _inputController.selection;
        final text = _inputController.text;
        final newText = text.replaceRange(selection.start, selection.end, value);
        _inputController.text = newText;
        _inputController.selection = TextSelection.collapsed(offset: selection.start + value.length);
        _expression = _inputController.text;
      });
    }
  }

  void _showBmiDialog() async {
    final weightController = TextEditingController();
    final heightController = TextEditingController();
    await showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('BMI Calculator'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: weightController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Weight (kg)',
                ),
              ),
              TextField(
                controller: heightController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Height (cm)',
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                final weight = double.tryParse(weightController.text);
                final heightCm = double.tryParse(heightController.text);
                if (weight != null && heightCm != null && heightCm > 0) {
                  final heightM = heightCm / 100;
                  final bmi = weight / (heightM * heightM);
                  setState(() {
                    _result = 'BMI: ' + bmi.toStringAsFixed(2);
                    _expression = '';
                  });
                  Navigator.of(context).pop();
                }
              },
              child: const Text('Calculate'),
            ),
          ],
        );
      },
    );
  }

  String _evaluate(String expr) {
    try {
      // Replace only the sqrt symbol
      expr = expr.replaceAll('√', 'sqrt');
      expr = expr.replaceAll('×', '*').replaceAll('÷', '/');
      // Convert trig functions to radians if in the form func(...)
      expr = expr.replaceAllMapped(
        RegExp(r'(sin|cos|tan)\(([^)]+)\)'),
        (match) {
          final func = match.group(1);
          final arg = match.group(2);
          return '$func((${arg})*pi/180)';
        },
      );
      Parser p = Parser();
      Expression exp = p.parse(expr);
      ContextModel cm = ContextModel();
      double eval = exp.evaluate(EvaluationType.REAL, cm);
      return eval.toString();
    } catch (e) {
      return 'Error: Check parentheses and function usage.';
    }
  }

  Widget _buildButton(String text, {Color? color}) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.all(4.0),
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: color ?? Colors.deepPurple,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 20),
          ),
          onPressed: () => _onButtonPressed(text),
          child: Text(text, style: const TextStyle(fontSize: 20)),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: TextField(
              controller: _inputController,
              focusNode: _inputFocusNode,
              style: const TextStyle(fontSize: 28, color: Colors.black54),
              textAlign: TextAlign.right,
              decoration: const InputDecoration(border: OutlineInputBorder()),
              onChanged: (val) {
                setState(() {
                  _expression = val;
                });
              },
            ),
          ),
          Container(
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              _result,
              style: const TextStyle(fontSize: 36, color: Colors.black),
            ),
          ),
          const Divider(),
          Expanded(
            child: Column(
              children: [
                Row(
                  children: [
                    _buildButton('('),
                    _buildButton(')'),
                    _buildButton('AC', color: Colors.red),
                    _buildButton('⌫', color: Colors.orange),
                    _buildButton('BMI', color: Colors.teal),
                  ],
                ),
                Row(
                  children: [
                    _buildButton('7'),
                    _buildButton('8'),
                    _buildButton('9'),
                    _buildButton('/', color: Colors.orange),
                    _buildButton('sin', color: Colors.green),
                  ],
                ),
                Row(
                  children: [
                    _buildButton('4'),
                    _buildButton('5'),
                    _buildButton('6'),
                    _buildButton('*', color: Colors.orange),
                    _buildButton('cos', color: Colors.green),
                  ],
                ),
                Row(
                  children: [
                    _buildButton('1'),
                    _buildButton('2'),
                    _buildButton('3'),
                    _buildButton('-', color: Colors.orange),
                    _buildButton('tan', color: Colors.green),
                  ],
                ),
                Row(
                  children: [
                    _buildButton('0'),
                    _buildButton('.'),
                    _buildButton('C', color: Colors.red),
                    _buildButton('+', color: Colors.orange),
                    _buildButton('log', color: Colors.green),
                  ],
                ),
                Row(
                  children: [
                    _buildButton('√', color: Colors.green),
                    _buildButton('=', color: Colors.blue),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
