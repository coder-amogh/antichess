import unittest
from antichess.Board import Board
from antichess import Pieces
from antichess.Rules import Suicide
from antichess.Move import Move

class EnPassantTest(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.rules = Suicide()

    def assertValidMoves(self, board, moves, colour, enforceCaptures=True):
        self.board.displayAsText()
        v, _ = self.rules.getAllValidMoves(self.board, colour, enforceCaptures)
        v_str = map(str, v)
        moves_str = map(str, moves)
        print "Generated: ", v_str
        print "Asserted: ", moves_str
        self.assertTrue(set(v_str)==set(moves_str))

    def testHasCaptures(self):
        self.board.clear()
        self.board.setPiece("a5", Pieces.Pawn(0))
        self.board.setPiece("b7", Pieces.Pawn(1))
        self.assertFalse(self.board.hasCaptures(0))
        self.board.makeMove(Move.fromNotation("b7b5", 1))
        self.assertTrue(self.board.hasCaptures(0))

    def testEnPassantCapture(self):
        self.board.clear()
        # Before en passant
        self.board.setPiece("a5", Pieces.Pawn(0))
        self.board.setPiece("b7", Pieces.Pawn(1))
        self.board.makeMove(Move.fromNotation("b7b5", 1))
        self.assertValidMoves(self.board, ["a5b6"], 0)
        # Check black pawn on b5
        self.assertTrue(isinstance(self.board.pieces[25], Pieces.Pawn))
        self.board.makeMove(Move.fromNotation("a5b6", 0))
        # Check pawn is gone
        self.board.displayAsText()
        self.assertTrue(self.board.pieces[25]==None)
        self.assertValidMoves(self.board, ["b6b7"], 0)
        self.assertValidMoves(self.board, [], 1)
        # Check undo
        print map(str,self.board.movesMade[-1])
        print self.board.getLastMovedPiece().colour
        self.board.retractMove()
        print map(str,self.board.movesMade[-1])
        print self.board.getLastMovedPiece().colour
        self.board.displayAsText()
        self.assertTrue(isinstance(self.board.pieces[25], Pieces.Pawn))
        self.assertEquals(self.board.pieces[25].colour, 1)

    def testEnPassantWhite(self):
        self.board.clear()
        # Before en passant
        self.board.setPiece("a5", Pieces.Pawn(0))
        self.board.setPiece("b7", Pieces.Pawn(1))
        self.board.setPiece("h3", Pieces.Pawn(0))
        self.assertValidMoves(self.board, ["a5a6", "h3h4"], 0)
        # En passant opportunity
        self.board.makeMove(Move.fromNotation("b7b5", 1))
        self.assertValidMoves(self.board, ["a5b6"], 0)
        self.assertValidMoves(self.board, ["a5a6", "a5b6", "h3h4"], 0, enforceCaptures=False)
        # Opportunity passed
        self.board.makeMove(Move.fromNotation("h3h4", 0))
        self.assertValidMoves(self.board, ["a5a6", "h4h5"], 0)

    def testEnPassantBlack(self):
        self.board.clear()
        # Before en passant
        self.board.setPiece("a4", Pieces.Pawn(1))
        self.board.setPiece("b2", Pieces.Pawn(0))
        self.board.setPiece("h4", Pieces.Pawn(1))
        self.assertValidMoves(self.board, ["a4a3", "h4h3"], 1)
        # En passant opportunity
        self.board.makeMove(Move.fromNotation("b2b4", 0))
        self.assertValidMoves(self.board, ["a4b3"], 1)
        self.assertValidMoves(self.board, ["a4a3", "a4b3", "h4h3"], 1, enforceCaptures=False)
        # Opportunity passed
        self.board.makeMove(Move.fromNotation("h4h3", 1))
        self.assertValidMoves(self.board, ["a4a3", "h3h2"], 1)

    def testEnPassantRegistersAsCapture(self):
        self.board.clear()
        # Before en passant
        self.board.setPiece("a4", Pieces.Pawn(1))
        self.board.setPiece("b2", Pieces.Pawn(0))
        self.board.setPiece("h4", Pieces.Pawn(1))
        self.assertValidMoves(self.board, ["a4a3", "h4h3"], 1)
        # En passant opportunity
        self.board.makeMove(Move.fromNotation("b2b4", 0))
        self.assertValidMoves(self.board, ["a4b3"], 1)
        self.assertValidMoves(self.board, ["a4a3", "a4b3", "h4h3"], 1, enforceCaptures=False)
        # Check it registers as a capture opportunity
        _, iscap = self.rules.getAllValidMoves(self.board, 1, enforceCaptures=True)
        self.assertEqual(len(iscap), 1)
        self.assertEqual(iscap[0], 1)
        # Check we have captures
        self.assertTrue(self.board.hasCaptures(1))
        # Opportunity passed
        self.board.makeMove(Move.fromNotation("h4h3", 1))
        _, iscap = self.rules.getAllValidMoves(self.board, 1, enforceCaptures=True)
        self.assertEqual(len(iscap), 2)
        self.assertEqual(sum(iscap), 0)

    def testEnPassantWhiteUndo(self):
        self.board.clear()
        # Before en passant
        self.board.setPiece("a5", Pieces.Pawn(0))
        self.board.setPiece("b7", Pieces.Pawn(1))
        self.board.setPiece("h3", Pieces.Pawn(0))
        self.assertValidMoves(self.board, ["a5a6", "h3h4"], 0)
        # En passant opportunity
        self.board.makeMove(Move.fromNotation("b7b5", 1))
        self.assertValidMoves(self.board, ["a5b6"], 0)
        # Opportunity passed
        self.board.makeMove(Move.fromNotation("h3h4", 0))
        self.assertValidMoves(self.board, ["a5a6", "h4h5"], 0)
        # Undo h3h4
        self.board.retractMove()
        # Opportunity re-appears
        self.assertValidMoves(self.board, ["a5b6"], 0, enforceCaptures=True)
        self.assertValidMoves(self.board, ["a5a6", "a5b6", "h3h4"], 0, enforceCaptures=False)
        # Try lots of undos
        self.board.makeMove(Move.fromNotation("h3h4", 0))
        self.board.makeMove(Move.fromNotation("h4h5", 0))
        self.board.makeMove(Move.fromNotation("b5b4", 1))
        self.board.makeMove(Move.fromNotation("h5h6", 0))
        self.board.makeMove(Move.fromNotation("b4b3", 1))
        self.board.makeMove(Move.fromNotation("h7h8", 0))
        self.board.retractMove()
        self.board.retractMove()
        self.board.retractMove()
        self.board.retractMove()
        self.board.retractMove()
        # Not valid yet...
        self.assertValidMoves(self.board, ["a5a6", "h4h5"], 0)
        self.board.retractMove()
        # Now valid en passant
        self.assertValidMoves(self.board, ["a5b6"], 0)

    def testDoubleEnpassant(self):
        self.board.clear()
        self.board.setPiece("c4", Pieces.Pawn(1))
        self.board.setPiece("e4", Pieces.Pawn(1))
        self.board.setPiece("d2", Pieces.Pawn(0))
        self.assertValidMoves(self.board, ["c4c3", "e4e3"], 1)
        # Double en passant opportunity
        self.board.makeMove(Move.fromNotation("d2d4", 0))
        self.assertValidMoves(self.board, ["c4d3", "e4d3"], 1)
        self.assertValidMoves(self.board, ["c4c3", "c4d3", "e4e3", "e4d3"], 1, enforceCaptures=False)
        # Pass
        self.board.makeMove(Move.fromNotation("c4c3", 1))
        self.assertValidMoves(self.board, ["c3c2", "e4e3"], 1)
        # Undo
        self.board.retractMove()
        self.assertValidMoves(self.board, ["c4d3", "e4d3"], 1, enforceCaptures=True)
        self.assertValidMoves(self.board, ["c4c3", "c4d3", "e4e3", "e4d3"], 1, enforceCaptures=False)

if __name__=="__main__":
    unittest.main()
