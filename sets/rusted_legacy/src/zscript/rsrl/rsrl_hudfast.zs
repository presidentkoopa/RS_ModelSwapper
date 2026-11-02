// RSRL fast HUD (RSQ Weapon Depot, step S4): his watch and gun display, drawn the same, without the per-tic cost.
//
// His DoomWeaponZ.Tick, every tic, for the ready weapon:
//   - turns ammo, health and armor into strings to find the digits (calculateHUDValues)
//   - destroys and re-creates the 17 HUD layers and the laser layer (17 + 1 new PSprite objects per tic)
//   - runs each new layer's chain of up to 13 A_JumpIf states to pick its frame
//   - resolves up to 10 state labels by name (CheckWeaponState) and re-sets 3 inventory counts
// Here, with rsrl_hudfast 1 (default):
//   - calculateHUDValues (his, unchanged) runs only when one of its inputs changed
//   - each layer is made once and then only gets its sprite and frame set; the frame comes from his own state
//     chains compiled to functions (rsrl_hudfast_table.zs, tools/gen_hudfast.py), so it is the frame his
//     chain would show
//   - his overlay style calls run once when a layer is made, in his order (the dial ends Add 0.8, as his
//     hud_bracer leaves it; the panel background Translucent 0.7)
//   - the laser layer is kept while it is wanted and re-made only when his laser settings change
//   - the state labels are resolved once per weapon
// rsrl_hudfast 0 runs his original code. rsrl_hudcheck 1 runs his original code AND the compiled chains every
// tic and logs any layer where they differ. rsrl_hudprof 1 logs the average cost of this part of Tick.

extend class DoomWeaponZ
{
	Array<int> rshSpr;			// SpriteID per RSH sprite index, 0 = not looked up yet
	Array<int> rshVar;			// SpriteID per (pose * BASES + base), 0 = not looked up yet
	int rshTNT1;
	int rshDialStyle;
	Array<State> rshLab;		// his labels, resolved once
	bool rshLabOk;
	int rshSig[12];				// inputs of calculateHUDValues last time
	bool rshSigOk;
	bool rshValuesChanged;
	int rshDraw[12];			// what the 17 layers were last drawn from (values, settings, pose)
	bool rshDrawOk;
	transient CVar rshCvFollow, rshCvFast, rshCvCheck, rshCvProf;
	int rshLaserColor;
	double rshLaserAlpha;
	int rshPoseSpr, rshPoseFrm, rshPose;
	double rshProfT;
	int rshProfN;
	int rshCheckBad, rshCheckN;

	const RSH_FIRST = 1050;
	const RSH_LAST = 1066;

	States
	{
	RSH_Hold:
		TNT1 A -1;
		Stop;
	RSH_HoldB:
		TNT1 A -1 Bright;
		Stop;
	// his overlay calls, as his Tick leaves them each tic: hud_bg sets the dial Translucent 0.7, hud_bracer
	// sets the bracer's flags and the dial Add 0.8, then whud_bg (gun display on) sets the dial Translucent 0.7
	// again. So the dial ends Translucent 0.7 with the gun display on, Add 0.8 with it off; the panel keeps
	// the default style (whud_bg's calls name the dial layer, not the panel).
	RSH_StyleDialT:
		TNT1 A 0 A_OverlayFlags(1050, PSPF_RENDERSTYLE | PSPF_FORCEALPHA, true);
		TNT1 A 0 A_OverlayRenderStyle(1050, STYLE_Translucent);
		TNT1 A 0 A_OverlayAlpha(1050, 0.7);
		Goto RSH_Hold;
	RSH_StyleDialA:
		TNT1 A 0 A_OverlayFlags(1050, PSPF_RENDERSTYLE | PSPF_FORCEALPHA, true);
		TNT1 A 0 A_OverlayRenderStyle(1050, STYLE_Add);
		TNT1 A 0 A_OverlayAlpha(1050, 0.8);
		Goto RSH_Hold;
	RSH_StyleBelt:
		TNT1 A 0 A_OverlayFlags(1051, PSPF_RENDERSTYLE | PSPF_FORCEALPHA, true);
		Goto RSH_Hold;
	}

	static int RSH_CVar(PlayerInfo p, name n, int def)
	{
		let cv = CVar.GetCVar(n, p);
		return cv ? cv.GetInt() : def;
	}

	// which of his entry labels each layer starts at (his setWatchHUD / setWeaponHUD)
	int RSH_Entry(int layer)
	{
		switch (layer)
		{
		case 1050: return RSH_hud_bg();
		case 1051: return RSH_hud_bracer();
		case 1052: return RSH_hud_hp_bar();
		case 1053: return RSH_hud_counter1();
		case 1054: return RSH_hud_counter2();
		case 1055: return RSH_hud_counter3();
		case 1056: return RSH_hud_armor_bar();
		case 1057: return RSH_hud_counter4();
		case 1058: return RSH_hud_counter5();
		case 1059: return RSH_hud_counter6();
		case 1060: return RSH_whud_bg();
		case 1061: return RSH_whud_mag_d1();
		case 1062: return RSH_whud_mag_d2();
		case 1063: return RSH_whud_mag_d3();
		case 1064: return RSH_whud_mag_d4();
		case 1065: return RSH_whud_mag_d5();
		case 1066: return RSH_whud_mag_d6();
		}
		return -1;
	}

	int RSH_SpriteID(int i)
	{
		if (rshSpr.Size() < RSH_NSPRITES)
		{
			rshSpr.Resize(RSH_NSPRITES);
			for (int k = 0; k < RSH_NSPRITES; k++)
				rshSpr[k] = 0;
		}
		if (!rshSpr[i])
			rshSpr[i] = GetSpriteIndex(RSH_SpriteName(i));
		return rshSpr[i];
	}

	// pose v's copy of a HUD sprite (rsrl_hudfollow), cached; the sprite itself when it has none
	int RSH_PoseSprite(int spr, int v)
	{
		if (v <= 0)
			return spr;
		int nb = RSRL_HudFollow.BASES;
		if (rshVar.Size() < (RSRL_HudFollow.POSES + 1) * nb)
		{
			int n = (RSRL_HudFollow.POSES + 1) * nb;
			rshVar.Resize(n);
			for (int k = 0; k < n; k++)
				rshVar[k] = 0;
		}
		for (int b = 0; b < nb; b++)
		{
			int k = b;		// base sprite IDs live in pose row 0
			if (!rshVar[k])
				rshVar[k] = GetSpriteIndex(RSRL_HudFollow.BaseName(b));
			if (rshVar[k] != spr)
				continue;
			k = v * nb + b;
			if (!rshVar[k])
				rshVar[k] = GetSpriteIndex(RSRL_HudFollow.VarName(v, b));
			return rshVar[k];
		}
		return spr;
	}

	// his calculateHUDValues, only when its inputs changed
	void RSH_Values(PlayerInfo player)
	{
		let pmo = player.mo;
		Ammo a1, a2;
		if (player.ReadyWeapon == self)
		{
			a1 = player.ReadyWeapon.Ammo1;
			a2 = player.ReadyWeapon.Ammo2;
		}
		else if (player.OffhandWeapon == self)
		{
			a1 = player.OffhandWeapon.Ammo1;
			a2 = player.OffhandWeapon.Ammo2;
		}
		int s[12];
		s[0] = a1 ? a1.Amount : -99999;
		s[1] = a2 ? a2.Amount : -99999;
		s[2] = pmo.health;
		s[3] = pmo.CountInv("BasicArmor");
		s[4] = wristWatchMode;
		s[5] = pmo.bInvulnerable;
		s[6] = player.cheats & (CF_GODMODE | CF_GODMODE2 | CF_INFINITEAMMO);
		bool same = rshSigOk;
		for (int i = 0; i < 7; i++)
		{
			if (rshSig[i] != s[i])
				same = false;
			rshSig[i] = s[i];
		}
		rshSigOk = true;
		rshValuesChanged = !same;
		if (!same)
			calculateHUDValues(player);
	}

	void RSH_Layer(PlayerInfo p, int layer, int pose)
	{
		int code = RSH_Entry(layer);
		let psp = p.FindPSprite(layer);
		int dstyle = WeaponHUDEnabled ? 1 : 2;
		if (!psp || psp.Caller != self || (layer == 1050 && rshDialStyle != dstyle))
		{
			psp = p.GetPSprite(layer);
			psp.Caller = self;
			State st = ResolveState("RSH_Hold");
			if (layer == 1050)
			{
				st = dstyle == 1 ? ResolveState("RSH_StyleDialT") : ResolveState("RSH_StyleDialA");
				rshDialStyle = dstyle;
			}
			else if (layer == 1051)
				st = ResolveState("RSH_StyleBelt");
			psp.SetState(st);
		}
		bool bright = code >= 0 && (code & 1);
		if (psp.CurState && psp.CurState.bFullbright != bright)
			psp.SetState(bright ? ResolveState("RSH_HoldB") : ResolveState("RSH_Hold"));
		if (code < 0)
		{
			if (!rshTNT1)
				rshTNT1 = GetSpriteIndex('TNT1');
			psp.Sprite = rshTNT1;
			psp.Frame = 0;
			return;
		}
		psp.Sprite = RSH_PoseSprite(RSH_SpriteID(code >> 8), pose);
		psp.Frame = (code >> 1) & 127;
	}

	void RSH_ClearRange(PlayerInfo p, int a, int b)
	{
		for (int l = a; l <= b; l++)
		{
			let psp = p.FindPSprite(l);
			if (psp)
				psp.Destroy();
		}
	}

	// his CheckWeaponState labels, resolved once per weapon: 0-8 the reload states that hold the laser off, 9 Ready
	void RSH_Labels()
	{
		if (rshLabOk)
			return;
		rshLabOk = true;
		rshLab.Clear();
		rshLab.Push(FindState("Reload"));
		rshLab.Push(FindState("InsertAmmo"));
		rshLab.Push(FindState("ReloadNoShells"));
		rshLab.Push(FindState("ReloadLeft"));
		rshLab.Push(FindState("UnloadAmmo"));
		rshLab.Push(FindState("OpenBarrel"));
		rshLab.Push(FindState("WaitReload"));
		rshLab.Push(FindState("ImmersiveReloadMag"));
		rshLab.Push(FindState("ImmersiveReloadWait2"));
		rshLab.Push(FindState("Ready"));
	}

	// the ready-weapon part of his Tick, without the per-tic cost
	void RSH_Tick(PlayerInfo player)
	{
		RSH_Values(player);
		int pose = 0;
		let psw = player.FindPSprite(bOffhandWeapon ? PSP_OFFHANDWEAPON : PSP_WEAPON);
		if (!rshCvFollow)
			rshCvFollow = CVar.GetCVar('rsrl_hudfollow', player);
		if (!rshCvFollow || rshCvFollow.GetInt())
		{
			let pw = player.FindPSprite(PSP_WEAPON);
			if (pw)
			{
				if (pw.Sprite != rshPoseSpr || pw.Frame != rshPoseFrm)
				{
					rshPoseSpr = pw.Sprite;
					rshPoseFrm = pw.Frame;
					rshPose = RSRL_HudFollow.Pose(self, pw.Sprite, pw.Frame);
				}
				pose = rshPose;
			}
		}
		// the layers only change when what they are drawn from changes: his values, his settings, the pose
		int d[12];
		d[0] = wristWatchEnabled;
		d[1] = WeaponHUDEnabled;
		d[2] = wristWatchColor;
		d[3] = wristWatchMode;
		d[4] = watchBracerEnabled;
		d[5] = weaponModel;
		d[6] = WeaponHUDScale;
		d[7] = WeaponHUDBG;
		d[8] = WeaponHUDColor;
		d[9] = pose;
		bool redraw = !rshDrawOk || rshValuesChanged;
		for (int i = 0; i < 10; i++)
		{
			if (rshDraw[i] != d[i])
				redraw = true;
			rshDraw[i] = d[i];
		}
		if (!redraw)
		{
			// still ours? (a weapon switch or his own code may have replaced them)
			let probe = player.FindPSprite(wristWatchEnabled ? 1050 : 1060);
			if ((wristWatchEnabled || WeaponHUDEnabled) && (!probe || probe.Caller != self))
				redraw = true;
		}
		rshDrawOk = true;
		if (redraw)
		{
			if (wristWatchEnabled)
			{
				for (int l = 1050; l <= 1059; l++)
					RSH_Layer(player, l, pose);
			}
			else
				RSH_ClearRange(player, 1050, 1059);
			if (WeaponHUDEnabled)
			{
				for (int l = 1060; l <= 1066; l++)
					RSH_Layer(player, l, pose);
			}
			else
				RSH_ClearRange(player, 1060, 1066);
		}

		if (rshCvCheck && rshCvCheck.GetInt() == 2)
			RSH_CheckFast(player, pose);

		RSH_Labels();
		State cur = psw ? psw.CurState : null;
		bool reloading = false;
		for (int i = 0; i < 9 && cur; i++)
		{
			if (rshLab[i] && InStateSequence(cur, rshLab[i]))
			{
				reloading = true;
				break;
			}
		}
		if (reloading)
			laserActivateDelay = 35;
		if (laserActivateDelay)
			laserActivateDelay--;
		if (aimLaser && !laserActivateDelay)
		{
			let lp = player.FindPSprite(PSP_Laser_Pointer);
			if (!lp || lp.Caller != self || laserColor != rshLaserColor || laserAlpha != rshLaserAlpha)
			{
				clearLaserPointer(player);
				setLaserPointer(player);
				rshLaserColor = laserColor;
				rshLaserAlpha = laserAlpha;
			}
		}
		else
			clearLaserPointer(player);

		if (cur && rshLab[9] && InStateSequence(cur, rshLab[9]))
		{
			if (owner.CountInv("ImmersiveInteractToken")) owner.SetInventory("ImmersiveInteractToken", 0);
			if (owner.CountInv("ImmersiveReloadStep")) owner.SetInventory("ImmersiveReloadStep", 0);
			if (owner.CountInv("grabbedAmmo")) owner.SetInventory("grabbedAmmo", 0);
			if (marker1) marker1.Destroy();
			if (marker2) marker2.Destroy();
		}
	}

	// rsrl_hudcheck: his layers (just made by his code) against the compiled chains
	void RSH_Check(PlayerInfo p)
	{
		for (int l = 1050; l <= 1066; l++)
		{
			let psp = p.FindPSprite(l);
			if (!psp)
				continue;
			int his = -1;
			if (!rshTNT1)
				rshTNT1 = GetSpriteIndex('TNT1');
			if (psp.Sprite != rshTNT1)
			{
				his = -2;
				for (int i = 0; i < RSH_NSPRITES; i++)
				{
					if (RSH_SpriteID(i) == psp.Sprite)
					{
						his = (i << 8) | (psp.Frame << 1) | (psp.CurState && psp.CurState.bFullbright ? 1 : 0);
						break;
					}
				}
			}
			int mine = RSH_Entry(l);
			rshCheckN++;
			if (his != mine)
			{
				rshCheckBad++;
				if (rshCheckBad <= 20)
					Console.Printf("RSHCHECK %s layer %d: his %d mine %d", GetClassName(), l, his, mine);
			}
		}
		if (rshCheckN >= 17 * 35)
		{
			Console.Printf("RSHCHECK %s: %d layer-tics compared, %d differ", GetClassName(), rshCheckN, rshCheckBad);
			rshCheckN = 0;
		}
	}

	// rsrl_hudcheck 2: the fast path's layers, after any skipped redraw, against the compiled chains right now
	void RSH_CheckFast(PlayerInfo p, int pose)
	{
		for (int l = 1050; l <= 1066; l++)
		{
			bool on = l < 1060 ? wristWatchEnabled : WeaponHUDEnabled;
			let psp = p.FindPSprite(l);
			int code = RSH_Entry(l);
			bool ok;
			if (!on)
				ok = !psp;
			else if (!psp)
				ok = false;
			else if (code < 0)
				ok = psp.Sprite == rshTNT1;
			else
				ok = psp.Sprite == RSH_PoseSprite(RSH_SpriteID(code >> 8), pose) && psp.Frame == ((code >> 1) & 127)
					&& psp.CurState && psp.CurState.bFullbright == ((code & 1) != 0) && psp.Caller == self;
			rshCheckN++;
			if (!ok)
			{
				rshCheckBad++;
				if (rshCheckBad <= 20)
					Console.Printf("RSHCHECK2 %s layer %d pose %d: wrong (code %d)", GetClassName(), l, pose, code);
			}
		}
		if (rshCheckN >= 17 * 35)
		{
			Console.Printf("RSHCHECK2 %s: %d layer-tics checked, %d wrong", GetClassName(), rshCheckN, rshCheckBad);
			rshCheckN = 0;
		}
	}

	void RSH_Prof(PlayerInfo p, double t0, bool fast)
	{
		rshProfT += MSTimeF() - t0;
		if (++rshProfN >= 350)
		{
			Console.Printf("RSHPROF %s %s: %.2f us per tic", GetClassName(), fast ? "fast" : "his", 1000.0 * rshProfT / rshProfN);
			rshProfT = 0;
			rshProfN = 0;
		}
	}
}
