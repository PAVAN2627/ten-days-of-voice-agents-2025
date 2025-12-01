import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

export async function POST(request: NextRequest) {
  try {
    const { filename, content, playerName, gameState } = await request.json();

    // Create saves directory if it doesn't exist
    const savesDir = join(process.cwd(), '..', 'backend', 'game_saves');
    
    if (!existsSync(savesDir)) {
      await mkdir(savesDir, { recursive: true });
    }

    // Save the file
    const filePath = join(savesDir, filename);
    await writeFile(filePath, content, 'utf-8');

    console.log(`Game saved: ${filename}`);
    console.log(`Player: ${playerName}, Rounds: ${gameState.current_round}/${gameState.max_rounds}`);

    return NextResponse.json({ 
      success: true, 
      filename,
      path: filePath 
    });
  } catch (error) {
    console.error('Error saving game:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to save game' },
      { status: 500 }
    );
  }
}
