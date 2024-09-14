# Trap-prefered Chess AI

## Data Preparison
`download_pgns.py` is used for download pgn data.
After that, combine all the pgn files into one by concatenating them one by one. Then please follow the "Move Prediction" section to generate the data.

### Move Prediction

To create your own maia from a set of chess games in the PGN format:

1. Setup your environment
   1. (optional) Install the `conda` environment, [`maia_env.yml`](maia_env.yml)
   2. Make sure all the required packages are installed from `requirements.txt`
2. Convert the PGN into the training format
   1. Add the [`pgn-extract`](https://www.cs.kent.ac.uk/people/staff/djb/pgn-extract/) tool to your path
   2. ~~Add the [`trainingdata-tool`](https://github.com/DanielUranga/trainingdata-tool) to your path~~
   2. Add the [`trainingdata-tool`](https://github.com/DanielUranga/trainingdata-tool) to your path, the changed file are attached in this project, please compile it following the original repo.
   3. Run `move_prediction/pgn_to_trainingdata.sh PGN_FILE_PATH OUTPUT_PATH`
   4. Wait a bit as the processing is both IO and CPU intense
   5. The script will create a training and validation set, if you wish to train on the whole set copy the files from `OUTPUT_PATH/validation` to `OUTPUT_PATH/training`
3. Edit `move_prediction/maia_config.yml`
   1. Add  `OUTPUT_PATH/training/*/*` to `input_train`
   2. Add  `OUTPUT_PATH/validation/*/*` to `input_test`
   3. (optional) If you have multiple GPUS change the `gpu` filed to the one you are using
   4. (optional) You can also change all the other training parameters here, like the number of layers
4. Run the training script `move_prediction/train_maia.py PATH_TO_CONFIG`
5. (optional) You can use tensorboard to watch the training progress, the logs are in `runs/CONFIG_BASENAME/`
6. Once complete the final model will be in `models/CONFIG_BASENAME/` directory. It will be the one with the largest number
