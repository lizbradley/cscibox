import wx

import wizard



def dist_filename(sample, att):
    #complicated filename to enforce useful unique-ness
    return os.extsep.join(('dist{depth:.4f}_{attname}_{run}'.format(
                                depth=float(sample['depth'].rescale('cm').magnitude),
                                attname=att, run=sample['run']),
                           'csv')).replace(' ', '_')


def export_samples(exp_samples, LiPD=False, core_data=None):
    # This function will currently only export the viewed columns and samples
    # of the displayed core in the GUI. There are two main modes: LiPD True or
    # False.
    #
    # If LiPD is False (the default and used by 'Export Samples' in the
    # 'file' dropdown) then there will be .csv files with labeled columns
    # exported for each computation plan and each sample with
    # UncertainQuantities
    #
    # If LiPD is True (Used by 'Export LiPD' in the 'file' dropdown) then the
    # output files will be identical to those of the False condition with three
    # key differences:
    # 1. The columns do not have labels in the .csv files
    # 2. There is one extra 'metadata.json' file that stores all metadata,
    #    column information, and links to each of the appropriate .csv files
    # 3. All of the data is packaged using 'bagit' which is designed for
    #    archiving/transfering data with a built-in way to verify the data
    #
    # No matter what the status of LiPD the final folder will be compressed and
    # saved in the location the user selects.

    # add header labels -- need to use iterator to get computation_plan/id correct

    wildcard = "zip File (*.zip)|*.zip|"               \
               "tar File (*.tar)|*.tar|"               \
               "gzip'ed tar File (*.gztar)|*.gztar|"   \
               "bzip2'ed tar File (*.bztar)|*.bztar"

    dlg = wx.FileDialog(None, message="Save samples in ...", defaultDir=os.getcwd(),
                        defaultFile="samples.zip", wildcard=wildcard,
                        style=wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)
    dlg.SetFilterIndex(0)

    if dlg.ShowModal() == wx.ID_OK:
        tempdir = tempfile.mkdtemp()

        # set of the currently visible computation plans
        displayedRuns = set([i.run for i in exp_samples])

        # Make the .csv's and return the filenames
        csv_fnames = create_csvs(exp_samples, LiPD,
                                 tempdir, displayedRuns)
        temp_fnames = [i[0] for i in csv_fnames]

        # If this is a LiPD export, write the LiPD file
        if LiPD:
            fname_LiPD = create_LiPD_JSON(csv_fnames, core_data, tempdir)
            temp_fnames.append(fname_LiPD)

        savefile, ext = os.path.splitext(dlg.GetPath())

        os.chdir(tempdir)

        if LiPD:
            bag = bagit.make_bag(tempdir, {'Made By:':'Output Automatically Generated by CScibox',
                                          'Contact-Name':'TODO: FIX THIS'})
            #validate the bagging process and print out errors if there are any
            try:
                bag.validate()

            except bagit.BagValidationError, e:
                for d in e.details:
                    if isinstance(d, bag.ChecksumMismatch):
                        print "expected %s to have %s checksum of %s but found %s" % \
                            (e.path, e.algorithm, e.expected, e.found)

        result = shutil.make_archive(savefile, ext[1:])
        os.chdir(os.path.dirname(savefile))

        shutil.rmtree(tempdir)

    dlg.Destroy()


def create_csvs(exp_samples, noheaders,
                tempdir, displayedRuns):
    # function to create necessary .csv files for export
    row_dicts = {}
    keylist = {}
    dist_dicts = {}

    for run in displayedRuns:
        row_dicts[run] = []
        keylist[run] = set()
        # export columns applicable to displayed runs

    for sample in exp_samples:
        run = sample.run
        if run not in keylist:
            continue
        row_dict = {}

        for key, val in sample.iteritems():
            if val is None:
                continue
            keylist[run].add(key)
            if hasattr(val, 'magnitude'):
                row_dict[key] = val.magnitude
                mag = val.uncertainty.magnitude

                if len(mag) == 1:
                    err_att = '%s Error' % key
                    row_dict[err_att] = mag[0].magnitude

                    # append keylist
                    keylist[run].add(err_att)

                elif len(mag) == 2:
                    minus_err_att = '%s Error-' % key
                    row_dict[minus_err_att] = mag[0].magnitude
                    plus_err_att = '%s Error+' % key
                    row_dict[plus_err_att] = mag[1].magnitude

                    # append keylist
                    keylist[run].add(minus_err_att)
                    keylist[run].add(plus_err_att)

                if val.uncertainty.distribution:
                    # store the distribution data as x,y pairs
                    fname = dist_filename(sample, key)
                    d_key = fname.strip('.csv')

                    # add data to dictionary for later output
                    dist_dicts[d_key] = zip(val.uncertainty.distribution.x,
                        val.uncertainty.distribution.y)
            else:
                try:
                    # This apparently happens if it's a pq.Quantity object
                    row_dict[key] = val.magnitude
                except AttributeError:
                    row_dict[key] = val

        row_dicts[run].append(row_dict)

    # store output filenames here
    fnames = []

    for run in row_dicts:
        keys = list(keylist[run])
        if noheaders:
            rows = []
        else:
            rows = [keys]

        for row_dict in row_dicts[run]:
            rows.append([row_dict.get(key, '') or '' for key in keys])

        fname = run.replace(' ', '_') + ".csv"
        fnames.append((fname,keys))

        with open(os.path.join(tempdir, fname), 'wb') as sdata:
            csv.writer(sdata, quoting=csv.QUOTE_NONNUMERIC).writerows(rows)

        for fname, dist in dist_dicts.iteritems():
            fnames.append(fname + ".csv")

            dist.insert(0, ('x', 'y'))

            with open(os.path.join(tempdir, fname + ".csv"), 'wb') as distfile:
                csv.writer(distfile).writerows(dist)

    return fnames


def create_LiPD_JSON(names, mdata, tempdir):
    # function to create the .jsonld structure for LiPD output

    metadata = {"LiPDVersion": "1.2",
                "chronData": [],
                "paleoData": [],
                "dataSetName": mdata.name,
                "geo": {
                    "type": "Feature",
                    "geometry": {
                        "coordinates": [0,0],
                        "type": "Point"
                    }
                }
            }

    for i in names:
        metadata["chronData"].append({
            "filename":i[0],
            "columns":[
                    {"variableName":i[1][j],
                     "TSid": "CSB"+str(random.randrange(1000000)),
                     "number": j}
                      for j in range(len(i[1]))]
            })

    # write metadata
    mdfname = 'metadata.json'
    with open(os.path.join(tempdir, mdfname), 'w') as mdfile:
        # sort keys and add indenting so the file can have repeatable form
        # and can be more easily readable by humans
        mdfile.write(json.dumps(metadata, indent=2, sort_keys=True))

    return mdfname
