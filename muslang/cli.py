"""
Command-Line Interface for Muslang

Provides commands for compiling, checking, and playing Muslang compositions.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from muslang.parser import parse_muslang_file
from muslang.semantics import SemanticAnalyzer, SemanticError
from muslang.midi_gen import MIDIGenerator
from muslang.config import DEFAULT_MIDI_PPQ, DEFAULT_TEMPO


def main():
    """Main entry point for the muslang CLI"""
    parser = argparse.ArgumentParser(
        description='Muslang: A music composition DSL compiler',
        epilog='Examples:\n'
               '  muslang compile song.mus\n'
               '  muslang compile song.mus -o output.mid\n'
               '  muslang check song.mus\n'
               '  muslang play song.mus\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Compile command
    compile_parser = subparsers.add_parser(
        'compile',
        help='Compile .mus file to MIDI',
        description='Compile a Muslang source file to a MIDI file'
    )
    compile_parser.add_argument(
        'input',
        help='Input .mus file'
    )
    compile_parser.add_argument(
        '-o', '--output',
        help='Output MIDI file (default: <input>.mid)'
    )
    compile_parser.add_argument(
        '--ppq',
        type=int,
        default=DEFAULT_MIDI_PPQ,
        help=f'MIDI resolution in pulses per quarter note (default: {DEFAULT_MIDI_PPQ})'
    )
    compile_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print detailed compilation information'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check .mus file for errors',
        description='Validate Muslang source file syntax and semantics'
    )
    check_parser.add_argument(
        'input',
        help='Input .mus file'
    )
    check_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print detailed validation information'
    )
    
    # Play command
    play_parser = subparsers.add_parser(
        'play',
        help='Compile and play .mus file',
        description='Compile a Muslang file and play it through a MIDI player'
    )
    play_parser.add_argument(
        'input',
        help='Input .mus file'
    )
    play_parser.add_argument(
        '--player',
        default='fluidsynth',
        choices=['fluidsynth', 'timidity'],
        help='MIDI player to use (default: fluidsynth)'
    )
    play_parser.add_argument(
        '--soundfont',
        help='Path to soundfont file (for fluidsynth)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'compile':
        sys.exit(compile_file(args.input, args.output, args.ppq, args.verbose))
    elif args.command == 'check':
        sys.exit(check_file(args.input, args.verbose))
    elif args.command == 'play':
        sys.exit(play_file(args.input, args.player, args.soundfont))
    else:
        parser.print_help()
        sys.exit(1)


def compile_file(input_path: str, output_path: Optional[str], ppq: int, verbose: bool) -> int:
    """
    Compile .mus file to MIDI
    
    Args:
        input_path: Path to input .mus file
        output_path: Path to output .mid file (or None for auto)
        ppq: MIDI resolution (pulses per quarter note)
        verbose: Whether to print detailed information
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        input_file = Path(input_path)
        
        if not input_file.exists():
            print(f"❌ Error: File not found: {input_path}", file=sys.stderr)
            return 1
        
        if not input_file.suffix == '.mus':
            print(f"⚠️  Warning: Expected .mus file extension, got {input_file.suffix}")
        
        if verbose:
            print(f"📖 Reading {input_path}...")
        
        # Parse
        if verbose:
            print(f"🔍 Parsing...")
        
        ast = parse_muslang_file(input_file)
        
        if verbose:
            print(f"   Found {len(ast.events)} top-level instruments/sections")
        
        # Semantic analysis
        if verbose:
            print(f"🔬 Analyzing semantics...")
        
        analyzer = SemanticAnalyzer()
        ast = analyzer.analyze(ast)
        
        if analyzer.warnings:
            for warning in analyzer.warnings:
                print(f"⚠️  Warning: {warning}", file=sys.stderr)
        
        if verbose:
            print(f"   Analysis complete")
        
        # Generate MIDI
        if verbose:
            print(f"🎵 Generating MIDI (PPQ={ppq})...")
        
        if output_path is None:
            output_path = str(input_file.with_suffix('.mid'))
        
        generator = MIDIGenerator(ppq=ppq)
        generator.generate(ast, output_path)
        
        print(f"✅ Successfully compiled to {output_path}")
        return 0
    
    except FileNotFoundError as e:
        print(f"❌ Error: File not found: {e}", file=sys.stderr)
        return 1
    
    except SemanticError as e:
        print(f"❌ Semantic Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def check_file(input_path: str, verbose: bool) -> int:
    """
    Check .mus file for syntax and semantic errors
    
    Args:
        input_path: Path to input .mus file
        verbose: Whether to print detailed information
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        input_file = Path(input_path)
        
        if not input_file.exists():
            print(f"❌ Error: File not found: {input_path}", file=sys.stderr)
            return 1
        
        if verbose:
            print(f"📖 Reading {input_path}...")
        
        # Parse
        if verbose:
            print(f"🔍 Parsing...")
        
        ast = parse_muslang_file(input_file)
        
        if verbose:
            print(f"   ✓ Syntax is valid")
            print(f"   Found {len(ast.events)} top-level instruments/sections")
        
        # Semantic analysis
        if verbose:
            print(f"🔬 Analyzing semantics...")
        
        analyzer = SemanticAnalyzer()
        ast = analyzer.analyze(ast)
        
        if analyzer.warnings:
            if verbose:
                print(f"⚠️  Found {len(analyzer.warnings)} warning(s):")
            for warning in analyzer.warnings:
                print(f"   ⚠️  {warning}")
        
        if verbose:
            print(f"   ✓ Semantics are valid")
        
        print(f"✅ {input_path} is valid")
        return 0
    
    except FileNotFoundError as e:
        print(f"❌ Error: File not found: {e}", file=sys.stderr)
        return 1
    
    except SemanticError as e:
        print(f"❌ Semantic Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def play_file(input_path: str, player: str, soundfont: Optional[str]) -> int:
    """
    Compile and play .mus file
    
    Args:
        input_path: Path to input .mus file
        player: MIDI player to use ('fluidsynth' or 'timidity')
        soundfont: Path to soundfont file (for fluidsynth)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    import tempfile
    import subprocess
    import shutil
    
    try:
        # Check if player is available
        if not shutil.which(player):
            print(f"❌ Error: {player} is not installed or not in PATH", file=sys.stderr)
            print(f"   Install it with: sudo apt install {player}", file=sys.stderr)
            return 1
        
        # Compile to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_midi = f.name
        
        try:
            print(f"🎵 Compiling {input_path}...")
            result = compile_file(input_path, temp_midi, DEFAULT_MIDI_PPQ, False)
            
            if result != 0:
                return result
            
            print(f"▶️  Playing with {player}...")
            
            # Play with selected player
            if player == 'fluidsynth':
                # Determine soundfont path
                if soundfont is None:
                    # Try common soundfont locations
                    common_paths = [
                        '/usr/share/soundfonts/default.sf2',
                        '/usr/share/sounds/sf2/FluidR3_GM.sf2',
                        '/usr/share/soundfonts/FluidR3_GM.sf2',
                    ]
                    for path in common_paths:
                        if Path(path).exists():
                            soundfont = path
                            break
                    
                    if soundfont is None:
                        print(f"❌ Error: No soundfont found. Specify with --soundfont", file=sys.stderr)
                        return 1
                
                # Run fluidsynth
                subprocess.run([
                    'fluidsynth',
                    '-a', 'alsa',
                    '-m', 'alsa_seq',
                    '-g', '1.0',
                    soundfont,
                    temp_midi
                ], check=True)
            
            elif player == 'timidity':
                subprocess.run(['timidity', temp_midi], check=True)
            
            print(f"✅ Playback complete")
            return 0
        
        finally:
            # Clean up temporary file
            Path(temp_midi).unlink(missing_ok=True)
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {player}: {e}", file=sys.stderr)
        return 1
    
    except FileNotFoundError as e:
        print(f"❌ Error: File not found: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    main()
