"""
Image processing module for Jigsaw Puzzle Solver.
Handles image upload, splitting into pieces, and piece management.
"""

import base64
import io
from dataclasses import dataclass
from typing import List, Tuple
from PIL import Image
import numpy as np


@dataclass
class PuzzlePiece:
    """Represents a single puzzle piece with its image and edge data."""
    piece_id: int
    original_row: int
    original_col: int
    image_data: str  # base64 encoded
    top_edge: np.ndarray
    bottom_edge: np.ndarray
    left_edge: np.ndarray
    right_edge: np.ndarray


class JigsawPuzzle:
    """
    Manages a jigsaw puzzle by splitting an image into pieces and tracking their positions.
    """

    def __init__(self, image_path: str, grid_size: int = 20):
        self.grid_size = grid_size
        self.total_pieces = grid_size * grid_size
        self.pieces: List[PuzzlePiece] = []
        self.piece_width = 0
        self.piece_height = 0

        self._load_and_split_image(image_path)

    def _load_and_split_image(self, image_path: str) -> None:
        """Load image and split into grid pieces."""
        img = Image.open(image_path).convert('RGB')

        # Calculate piece dimensions
        width, height = img.size
        self.piece_width = width // self.grid_size
        self.piece_height = height // self.grid_size

        # Crop to exact grid size (remove any extra pixels)
        crop_width = self.piece_width * self.grid_size
        crop_height = self.piece_height * self.grid_size
        img = img.crop((0, 0, crop_width, crop_height))

        img_array = np.array(img)

        piece_id = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Extract piece region
                y_start = row * self.piece_height
                y_end = y_start + self.piece_height
                x_start = col * self.piece_width
                x_end = x_start + self.piece_width

                piece_array = img_array[y_start:y_end, x_start:x_end]

                # Extract edges for fitness calculation (average of edge pixels)
                # top/bottom: average the first/last 3 rows → shape (piece_width, 3)
                top_edge = np.mean(piece_array[0:3, :], axis=0)
                bottom_edge = np.mean(piece_array[-3:, :], axis=0)
                # left/right: average the first/last 3 columns → shape (piece_height, 3)
                left_edge = np.mean(piece_array[:, 0:3], axis=1)
                right_edge = np.mean(piece_array[:, -3:], axis=1)

                # Convert piece to base64
                piece_img = Image.fromarray(piece_array)
                buffer = io.BytesIO()
                piece_img.save(buffer, format='JPEG', quality=85)
                image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

                piece = PuzzlePiece(
                    piece_id=piece_id,
                    original_row=row,
                    original_col=col,
                    image_data=image_data,
                    top_edge=top_edge,
                    bottom_edge=bottom_edge,
                    left_edge=left_edge,
                    right_edge=right_edge
                )
                self.pieces.append(piece)
                piece_id += 1

    def get_pieces_data(self) -> List[dict]:
        """Return all pieces data for frontend."""
        return [
            {
                'piece_id': p.piece_id,
                'original_row': p.original_row,
                'original_col': p.original_col,
                'image_data': p.image_data
            }
            for p in self.pieces
        ]

    def get_random_arrangement(self) -> List[int]:
        """Return a random permutation of piece IDs."""
        indices = list(range(self.total_pieces))
        np.random.shuffle(indices)
        return indices

    def get_arrangement_images(self, arrangement: List[int]) -> List[str]:
        """
        Given an arrangement (chromosome), return the image data for each position.
        arrangement[i] = piece_id at position i
        """
        piece_map = {p.piece_id: p.image_data for p in self.pieces}
        return [piece_map[piece_id] for piece_id in arrangement]

    def get_correct_arrangement(self) -> List[int]:
        """Return the correct arrangement (pieces in order 0, 1, 2, ...)."""
        return list(range(self.total_pieces))
